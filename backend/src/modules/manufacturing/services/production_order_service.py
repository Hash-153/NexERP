"""
NexERP Production Work Order Lifecycle & Shop Floor Backflushing Engine.
Manages Work Order creation, component material reservations, routing job card dispatch,
material backflushing, and finished goods inventory receipt intake.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError, InsufficientStockError
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_PRODUCTION_COMPLETED
from backend.src.modules.manufacturing.models import (
    ProductionOrder,
    ProductionOrderMaterial,
    JobCard,
    BillOfMaterials,
    BOMLine,
    Routing,
    RoutingOperation
)
from backend.src.modules.manufacturing.schemas import ProductionOrderCreate
from backend.src.modules.manufacturing.enums import ProductionOrderStatus, JobCardStatus
from backend.src.modules.inventory.models import Item, Warehouse, WarehouseLocation
from backend.src.modules.inventory.services import StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate
from backend.src.modules.inventory.enums import MovementType


class ProductionOrderService:
    """
    Manufacturing Work Order controller.
    """

    @classmethod
    async def generate_order_number(cls, db: AsyncSession, tenant_id: str, start_date: date) -> str:
        year_str = str(start_date.year)
        prefix = f"WO-{year_str}-"
        query = select(ProductionOrder).where(ProductionOrder.tenant_id == tenant_id).order_by(ProductionOrder.order_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.order_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_production_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: ProductionOrderCreate,
        user_id: Optional[str] = None
    ) -> ProductionOrder:
        """
        Create Work Order, explode direct BOM components, and calculate required material allocations.
        """
        bom_query = select(BillOfMaterials).where(
            BillOfMaterials.id == payload.bom_id,
            BillOfMaterials.tenant_id == tenant_id
        ).options(selectinload(BillOfMaterials.lines).selectinload(BOMLine.item))
        b_res = await db.execute(bom_query)
        bom = b_res.scalar_one_or_none()

        if not bom:
            raise EntityNotFoundError("Bill of Materials not found.")

        order_num = await cls.generate_order_number(db, tenant_id, payload.start_date)

        wo = ProductionOrder(
            tenant_id=tenant_id,
            order_number=order_num,
            item_id=payload.item_id,
            bom_id=payload.bom_id,
            routing_id=payload.routing_id,
            warehouse_id=payload.warehouse_id,
            planned_quantity=payload.planned_quantity,
            completed_quantity=Decimal("0.0"),
            scrapped_quantity=Decimal("0.0"),
            start_date=payload.start_date,
            due_date=payload.due_date,
            status=ProductionOrderStatus.PLANNED.value
        )
        db.add(wo)
        await db.flush()

        # Add Component Material Requirements
        total_est_mat_cost = Decimal("0.0")
        for line in bom.lines:
            scrap_factor = Decimal("1.0") + (line.scrap_percentage / Decimal("100.0"))
            req_qty = (line.quantity / bom.quantity) * payload.planned_quantity * scrap_factor
            unit_c = line.item.standard_cost or line.item.moving_average_cost
            tot_c = req_qty * unit_c
            total_est_mat_cost += tot_c

            mat = ProductionOrderMaterial(
                tenant_id=tenant_id,
                production_order_id=wo.id,
                item_id=line.item_id,
                required_quantity=req_qty.quantize(Decimal("0.0001")),
                issued_quantity=Decimal("0.0"),
                unit_cost=unit_c,
                total_cost=tot_c
            )
            db.add(mat)

        wo.total_material_cost = total_est_mat_cost
        wo.total_production_cost = total_est_mat_cost
        wo.unit_cost = (total_est_mat_cost / payload.planned_quantity).quantize(Decimal("0.0001"))

        # If routing specified, generate Job Cards
        if payload.routing_id:
            r_res = await db.execute(
                select(Routing).where(Routing.id == payload.routing_id).options(selectinload(Routing.operations))
            )
            routing = r_res.scalar_one_or_none()
            if routing:
                for op in routing.operations:
                    jc_num = f"JC-{order_num}-{op.sequence_number}"
                    jc = JobCard(
                        tenant_id=tenant_id,
                        job_card_number=jc_num,
                        production_order_id=wo.id,
                        operation_id=op.id,
                        work_center_id=op.work_center_id,
                        planned_quantity=payload.planned_quantity,
                        completed_quantity=Decimal("0.0"),
                        scrapped_quantity=Decimal("0.0"),
                        status=JobCardStatus.PENDING.value
                    )
                    db.add(jc)

        await db.commit()
        await db.refresh(wo)
        return wo

    @classmethod
    async def complete_production_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        order_id: str,
        completed_quantity: Decimal,
        location_id: str,
        user_id: Optional[str] = None
    ) -> ProductionOrder:
        """
        Finalize Work Order: backflush materials from warehouse and intake finished goods into stock.
        """
        query = (
            select(ProductionOrder)
            .where(ProductionOrder.id == order_id, ProductionOrder.tenant_id == tenant_id)
            .options(
                selectinload(ProductionOrder.materials).selectinload(ProductionOrderMaterial.item),
                selectinload(ProductionOrder.item)
            )
        )
        res = await db.execute(query)
        wo = res.scalar_one_or_none()

        if not wo:
            raise EntityNotFoundError("Production order not found.")

        if wo.status == ProductionOrderStatus.COMPLETED.value:
            raise BusinessRuleViolationError("Production order is already completed.")

        # 1. Backflush: Goods Issue for all materials
        issue_lines = []
        loc_res = await db.execute(select(WarehouseLocation).where(WarehouseLocation.warehouse_id == wo.warehouse_id).limit(1))
        src_loc = loc_res.scalar_one_or_none()
        src_loc_id = src_loc.id if src_loc else location_id

        actual_mat_cost = Decimal("0.0")
        for mat in wo.materials:
            qty_to_issue = (mat.required_quantity / wo.planned_quantity) * completed_quantity
            mat.issued_quantity += qty_to_issue
            actual_mat_cost += (qty_to_issue * mat.unit_cost)

            issue_lines.append(
                StockMovementLineCreate(
                    item_id=mat.item_id,
                    source_location_id=src_loc_id,
                    quantity=qty_to_issue,
                    unit_cost=mat.unit_cost
                )
            )

        if issue_lines:
            issue_mov = StockMovementCreate(
                movement_type=MovementType.PRODUCTION_CONSUMPTION,
                movement_date=date.today(),
                source_warehouse_id=wo.warehouse_id,
                reference=wo.order_number,
                remarks=f"Material backflushing consumption for WO {wo.order_number}",
                lines=issue_lines
            )
            await StockMovementService.execute_movement(db, tenant_id, issue_mov, user_id)

        # 2. Finished Goods Receipt Intake
        unit_mfg_cost = (actual_mat_cost / completed_quantity).quantize(Decimal("0.0001"))
        receipt_lines = [
            StockMovementLineCreate(
                item_id=wo.item_id,
                target_location_id=location_id,
                quantity=completed_quantity,
                unit_cost=unit_mfg_cost
            )
        ]
        receipt_mov = StockMovementCreate(
            movement_type=MovementType.PRODUCTION_OUTPUT,
            movement_date=date.today(),
            target_warehouse_id=wo.warehouse_id,
            reference=wo.order_number,
            remarks=f"Finished goods manufacturing output for WO {wo.order_number}",
            lines=receipt_lines
        )
        mov = await StockMovementService.execute_movement(db, tenant_id, receipt_mov, user_id)

        wo.completed_quantity = completed_quantity
        wo.total_material_cost = actual_mat_cost
        wo.total_production_cost = actual_mat_cost
        wo.unit_cost = unit_mfg_cost
        wo.status = ProductionOrderStatus.COMPLETED.value
        wo.stock_movement_id = mov.id

        await db.commit()
        await db.refresh(wo)

        # Dispatch event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_PRODUCTION_COMPLETED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"order_id": wo.id, "order_number": wo.order_number, "completed_qty": float(completed_quantity)}
        ))

        return wo

    @classmethod
    async def list_orders(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 50) -> List[ProductionOrder]:
        query = (
            select(ProductionOrder)
            .where(ProductionOrder.tenant_id == tenant_id, ProductionOrder.is_deleted == False)
            .options(selectinload(ProductionOrder.materials))
            .order_by(ProductionOrder.start_date.desc(), ProductionOrder.order_number.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(query)
        return list(res.scalars().all())
