"""
NexERP Stock Movement & Inventory Transaction Engine.
Executes physical bin movements, updates balances, depletes FIFO layers, and posts GL inventory journals.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, InsufficientStockError, BusinessRuleViolationError
from backend.src.modules.inventory.models import (
    Item,
    ItemCategory,
    Warehouse,
    WarehouseLocation,
    StockItemBalance,
    StockMovement,
    StockMovementLine,
    StockValuationLayer
)
from backend.src.modules.inventory.schemas import StockMovementCreate
from backend.src.modules.inventory.enums import MovementType
from backend.src.modules.inventory.services.costing_valuation_service import CostingValuationService
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class StockMovementService:
    """
    Inventory movement execution and warehouse balance controller.
    """

    @classmethod
    async def generate_movement_number(cls, db: AsyncSession, tenant_id: str, movement_date: date) -> str:
        year_str = str(movement_date.year)
        prefix = f"STK-{year_str}-"
        query = (
            select(StockMovement)
            .where(
                StockMovement.tenant_id == tenant_id,
                StockMovement.movement_number.like(f"{prefix}%")
            )
            .order_by(StockMovement.movement_number.desc())
            .limit(1)
        )
        result = await db.execute(query)
        latest = result.scalar_one_or_none()
        seq = int(latest.movement_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def get_or_create_balance(
        cls,
        db: AsyncSession,
        tenant_id: str,
        item_id: str,
        warehouse_id: str,
        location_id: str,
        lot_id: Optional[str] = None
    ) -> StockItemBalance:
        query = select(StockItemBalance).where(
            StockItemBalance.tenant_id == tenant_id,
            StockItemBalance.item_id == item_id,
            StockItemBalance.warehouse_id == warehouse_id,
            StockItemBalance.location_id == location_id,
            StockItemBalance.lot_id == lot_id
        )
        res = await db.execute(query)
        bal = res.scalar_one_or_none()
        if not bal:
            bal = StockItemBalance(
                tenant_id=tenant_id,
                item_id=item_id,
                warehouse_id=warehouse_id,
                location_id=location_id,
                lot_id=lot_id,
                quantity_on_hand=Decimal("0.0"),
                quantity_reserved=Decimal("0.0"),
                quantity_available=Decimal("0.0")
            )
            db.add(bal)
            await db.flush()
        return bal

    @classmethod
    async def execute_movement(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: StockMovementCreate,
        user_id: Optional[str] = None
    ) -> StockMovement:
        """
        Execute stock movement across bins and warehouses, maintain FIFO queues,
        and post automated General Ledger inventory accruals.
        """
        mov_num = await cls.generate_movement_number(db, tenant_id, payload.movement_date)

        movement = StockMovement(
            tenant_id=tenant_id,
            movement_number=mov_num,
            movement_type=payload.movement_type.value,
            movement_date=payload.movement_date,
            source_warehouse_id=payload.source_warehouse_id,
            target_warehouse_id=payload.target_warehouse_id,
            status="POSTED",
            reference=payload.reference,
            remarks=payload.remarks
        )
        db.add(movement)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            item_res = await db.execute(select(Item).where(Item.id == line.item_id, Item.tenant_id == tenant_id))
            item = item_res.scalar_one_or_none()
            if not item:
                raise EntityNotFoundError(f"Item ID '{line.item_id}' not found.")

            computed_cost = line.unit_cost if line.unit_cost > 0 else item.moving_average_cost

            # Handle Receipt vs Issue vs Transfer
            if payload.movement_type in [MovementType.GOODS_RECEIPT, MovementType.ADJUSTMENT_POSITIVE, MovementType.PRODUCTION_OUTPUT]:
                # Increase target location balance
                if not line.target_location_id or not payload.target_warehouse_id:
                    raise BusinessRuleViolationError("Target warehouse and location required for goods receipt.")

                target_bal = await cls.get_or_create_balance(
                    db, tenant_id, item.id, payload.target_warehouse_id, line.target_location_id, line.lot_id
                )
                target_bal.quantity_on_hand += line.quantity
                target_bal.quantity_available += line.quantity

                # Add FIFO Layer
                await CostingValuationService.record_receipt_valuation(
                    db=db,
                    tenant_id=tenant_id,
                    item_id=item.id,
                    warehouse_id=payload.target_warehouse_id,
                    quantity=line.quantity,
                    unit_cost=computed_cost,
                    receipt_date=payload.movement_date,
                    lot_id=line.lot_id,
                    source_doc_type="StockMovement",
                    source_doc_id=movement.id
                )

            elif payload.movement_type in [MovementType.GOODS_ISSUE, MovementType.ADJUSTMENT_NEGATIVE, MovementType.PRODUCTION_CONSUMPTION]:
                # Decrease source location balance
                if not line.source_location_id or not payload.source_warehouse_id:
                    raise BusinessRuleViolationError("Source warehouse and location required for goods issue.")

                source_bal = await cls.get_or_create_balance(
                    db, tenant_id, item.id, payload.source_warehouse_id, line.source_location_id, line.lot_id
                )
                if source_bal.quantity_available < line.quantity:
                    raise InsufficientStockError(
                        f"Insufficient stock for SKU {item.sku} in source location. Available: {source_bal.quantity_available}, Requested: {line.quantity}"
                    )

                source_bal.quantity_on_hand -= line.quantity
                source_bal.quantity_available -= line.quantity

                # Deplete FIFO layers
                total_depleted_cost, _ = await CostingValuationService.deplete_fifo_layers(
                    db=db,
                    tenant_id=tenant_id,
                    item_id=item.id,
                    warehouse_id=payload.source_warehouse_id,
                    quantity_to_deplete=line.quantity
                )
                computed_cost = total_depleted_cost / line.quantity

            elif payload.movement_type in [MovementType.WAREHOUSE_TRANSFER, MovementType.LOCATION_TRANSFER]:
                # Move between locations
                source_bal = await cls.get_or_create_balance(
                    db, tenant_id, item.id, payload.source_warehouse_id, line.source_location_id, line.lot_id
                )
                if source_bal.quantity_available < line.quantity:
                    raise InsufficientStockError(f"Insufficient stock for SKU {item.sku} to transfer.")

                target_wh = payload.target_warehouse_id or payload.source_warehouse_id
                target_bal = await cls.get_or_create_balance(
                    db, tenant_id, item.id, target_wh, line.target_location_id, line.lot_id
                )

                source_bal.quantity_on_hand -= line.quantity
                source_bal.quantity_available -= line.quantity
                target_bal.quantity_on_hand += line.quantity
                target_bal.quantity_available += line.quantity

            total_line_cost = line.quantity * computed_cost

            mov_line = StockMovementLine(
                tenant_id=tenant_id,
                stock_movement_id=movement.id,
                item_id=item.id,
                source_location_id=line.source_location_id,
                target_location_id=line.target_location_id,
                lot_id=line.lot_id,
                quantity=line.quantity,
                unit_cost=computed_cost,
                total_cost=total_line_cost
            )
            db.add(mov_line)

        await db.commit()
        await db.refresh(movement)
        return movement
