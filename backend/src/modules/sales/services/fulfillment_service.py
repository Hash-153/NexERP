"""
NexERP Sales Order Fulfillment & Pick-Pack-Ship Delivery Service.
Generates delivery orders, updates fulfilled quantities, and triggers physical inventory goods issue movements.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.sales.models import SalesOrder, SalesOrderLine, FulfillmentDelivery, FulfillmentDeliveryLine
from backend.src.modules.sales.schemas import FulfillmentDeliveryCreate
from backend.src.modules.sales.enums import SalesOrderStatus, DeliveryStatus
from backend.src.modules.inventory.services import StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate
from backend.src.modules.inventory.enums import MovementType


class FulfillmentService:
    """
    Pick, Pack, and Ship warehouse dispatch engine.
    """

    @classmethod
    async def generate_delivery_number(cls, db: AsyncSession, tenant_id: str, dispatch_date: date) -> str:
        year_str = str(dispatch_date.year)
        prefix = f"DLV-{year_str}-"
        query = select(FulfillmentDelivery).where(FulfillmentDelivery.tenant_id == tenant_id).order_by(FulfillmentDelivery.delivery_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.delivery_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_fulfillment_delivery(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: FulfillmentDeliveryCreate,
        user_id: Optional[str] = None
    ) -> FulfillmentDelivery:
        """
        Create delivery shipment, update SO fulfilled quantities, and trigger inventory goods issue.
        """
        so_query = (
            select(SalesOrder)
            .where(SalesOrder.id == payload.sales_order_id, SalesOrder.tenant_id == tenant_id)
            .options(selectinload(SalesOrder.lines))
        )
        so_res = await db.execute(so_query)
        so = so_res.scalar_one_or_none()

        if not so:
            raise EntityNotFoundError("Sales order not found.")

        if so.status in [SalesOrderStatus.FULFILLED.value, SalesOrderStatus.CANCELLED.value]:
            raise BusinessRuleViolationError(f"Cannot fulfill sales order in status: {so.status}")

        so_lines_map = {l.id: l for l in so.lines}
        dlv_num = await cls.generate_delivery_number(db, tenant_id, payload.dispatch_date)

        delivery = FulfillmentDelivery(
            tenant_id=tenant_id,
            delivery_number=dlv_num,
            sales_order_id=so.id,
            customer_id=so.customer_id,
            warehouse_id=payload.warehouse_id,
            dispatch_date=payload.dispatch_date,
            carrier=payload.carrier,
            tracking_number=payload.tracking_number,
            status=DeliveryStatus.SHIPPED.value,
            notes=payload.notes
        )
        db.add(delivery)
        await db.flush()

        stock_issue_lines = []

        for line_data in payload.lines:
            so_line = so_lines_map.get(line_data.so_line_id)
            if not so_line:
                raise EntityNotFoundError(f"Sales order line '{line_data.so_line_id}' not found.")

            remaining_to_fulfill = so_line.quantity_ordered - so_line.quantity_fulfilled
            if line_data.quantity_shipped > remaining_to_fulfill:
                raise BusinessRuleViolationError(
                    f"Shipped quantity ({line_data.quantity_shipped}) exceeds unfulfilled quantity ({remaining_to_fulfill}) on line {so_line.line_number}."
                )

            so_line.quantity_fulfilled = so_line.quantity_fulfilled + line_data.quantity_shipped
            so_line.quantity_allocated = max(Decimal("0.0"), so_line.quantity_allocated - line_data.quantity_shipped)

            dlv_line = FulfillmentDeliveryLine(
                tenant_id=tenant_id,
                delivery_id=delivery.id,
                so_line_id=so_line.id,
                item_id=line_data.item_id,
                location_id=line_data.location_id,
                quantity_shipped=line_data.quantity_shipped
            )
            db.add(dlv_line)

            stock_issue_lines.append(
                StockMovementLineCreate(
                    item_id=line_data.item_id,
                    source_location_id=line_data.location_id,
                    quantity=line_data.quantity_shipped
                )
            )

        # Trigger automatic stock issue movement
        if stock_issue_lines:
            mov_payload = StockMovementCreate(
                movement_type=MovementType.GOODS_ISSUE,
                movement_date=payload.dispatch_date,
                source_warehouse_id=payload.warehouse_id,
                reference=dlv_num,
                remarks=f"Outbound dispatch shipment for SO {so.so_number}",
                lines=stock_issue_lines
            )
            mov = await StockMovementService.execute_movement(db, tenant_id, mov_payload, user_id)
            delivery.stock_movement_id = mov.id

        # Update Sales Order status
        all_fulfilled = all(l.quantity_fulfilled >= l.quantity_ordered for l in so.lines)
        if all_fulfilled:
            so.status = SalesOrderStatus.FULFILLED.value
        else:
            so.status = SalesOrderStatus.PARTIALLY_FULFILLED.value

        await db.commit()
        await db.refresh(delivery)
        return delivery
