"""
NexERP Goods Receipt Note (GRN) & Receiving Dock Inbound Service.
Records physical arrivals, updates PO received quantities, and auto-executes inventory stock receipts.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.procurement.models import (
    PurchaseOrder,
    PurchaseOrderLine,
    GoodsReceiptNote,
    GoodsReceiptLine
)
from backend.src.modules.procurement.schemas import GoodsReceiptNoteCreate
from backend.src.modules.procurement.enums import POStatus, GRNStatus
from backend.src.modules.inventory.services import StockMovementService
from backend.src.modules.inventory.schemas import StockMovementCreate, StockMovementLineCreate
from backend.src.modules.inventory.enums import MovementType


class GoodsReceiptService:
    """
    Receiving dock shipment logging and automated stock intake engine.
    """

    @classmethod
    async def generate_grn_number(cls, db: AsyncSession, tenant_id: str, receipt_date: date) -> str:
        year_str = str(receipt_date.year)
        prefix = f"GRN-{year_str}-"
        query = (
            select(GoodsReceiptNote)
            .where(
                GoodsReceiptNote.tenant_id == tenant_id,
                GoodsReceiptNote.grn_number.like(f"{prefix}%")
            )
            .order_by(GoodsReceiptNote.grn_number.desc())
            .limit(1)
        )
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.grn_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_goods_receipt(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: GoodsReceiptNoteCreate,
        user_id: Optional[str] = None
    ) -> GoodsReceiptNote:
        """
        Record receiving dock GRN, update PO received quantities, and execute inventory stock movement.
        """
        po_query = (
            select(PurchaseOrder)
            .where(PurchaseOrder.id == payload.po_id, PurchaseOrder.tenant_id == tenant_id)
            .options(selectinload(PurchaseOrder.lines))
        )
        po_res = await db.execute(po_query)
        po = po_res.scalar_one_or_none()

        if not po:
            raise EntityNotFoundError("Purchase order not found.")

        if po.status not in [POStatus.ISSUED.value, POStatus.PARTIALLY_RECEIVED.value, POStatus.APPROVED.value]:
            raise BusinessRuleViolationError(f"Cannot receive goods against PO in status: {po.status}")

        po_lines_map = {l.id: l for l in po.lines}
        grn_num = await cls.generate_grn_number(db, tenant_id, payload.receipt_date)

        grn = GoodsReceiptNote(
            tenant_id=tenant_id,
            grn_number=grn_num,
            po_id=po.id,
            vendor_id=po.vendor_id,
            warehouse_id=payload.warehouse_id,
            receipt_date=payload.receipt_date,
            carrier_tracking_number=payload.carrier_tracking_number,
            status=GRNStatus.ACCEPTED.value,
            notes=payload.notes
        )
        db.add(grn)
        await db.flush()

        stock_lines = []

        for line_data in payload.lines:
            po_line = po_lines_map.get(line_data.po_line_id)
            if not po_line:
                raise EntityNotFoundError(f"PO Line '{line_data.po_line_id}' not found.")

            # Update PO line received quantity
            po_line.quantity_received = po_line.quantity_received + line_data.quantity_accepted

            grn_line = GoodsReceiptLine(
                tenant_id=tenant_id,
                grn_id=grn.id,
                po_line_id=po_line.id,
                item_id=line_data.item_id,
                quantity_received=line_data.quantity_received,
                quantity_accepted=line_data.quantity_accepted,
                quantity_rejected=line_data.quantity_rejected,
                location_id=line_data.location_id,
                lot_number=line_data.lot_number
            )
            db.add(grn_line)

            if line_data.quantity_accepted > 0:
                stock_lines.append(
                    StockMovementLineCreate(
                        item_id=line_data.item_id,
                        target_location_id=line_data.location_id,
                        quantity=line_data.quantity_accepted,
                        unit_cost=po_line.unit_price
                    )
                )

        # Trigger automatic stock movement receipt
        if stock_lines:
            mov_payload = StockMovementCreate(
                movement_type=MovementType.GOODS_RECEIPT,
                movement_date=payload.receipt_date,
                target_warehouse_id=payload.warehouse_id,
                reference=grn_num,
                remarks=f"Inbound receipt from PO {po.po_number}",
                lines=stock_lines
            )
            mov = await StockMovementService.execute_movement(db, tenant_id, mov_payload, user_id)
            grn.stock_movement_id = mov.id

        # Update PO Overall Status
        all_received = all(l.quantity_received >= l.quantity_ordered for l in po.lines)
        if all_received:
            po.status = POStatus.RECEIVED.value
        else:
            po.status = POStatus.PARTIALLY_RECEIVED.value

        await db.commit()
        await db.refresh(grn)
        return grn
