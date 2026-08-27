"""
NexERP Purchase Order Management & Workflow Engine.
Handles PO issuance, line-item pricing, multi-stage approval threshold evaluation, and delivery tracking.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_PO_APPROVED
from backend.src.modules.procurement.models import PurchaseOrder, PurchaseOrderLine
from backend.src.modules.procurement.schemas import PurchaseOrderCreate
from backend.src.modules.procurement.enums import POStatus
from backend.src.modules.accounts_payable.models import Vendor
from backend.src.modules.inventory.models import Item


class PurchaseOrderService:
    """
    Purchase Order lifecycle service.
    """

    @classmethod
    async def generate_po_number(cls, db: AsyncSession, tenant_id: str, order_date: date) -> str:
        year_str = str(order_date.year)
        prefix = f"PO-{year_str}-"
        query = (
            select(PurchaseOrder)
            .where(
                PurchaseOrder.tenant_id == tenant_id,
                PurchaseOrder.po_number.like(f"{prefix}%")
            )
            .order_by(PurchaseOrder.po_number.desc())
            .limit(1)
        )
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.po_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_purchase_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: PurchaseOrderCreate,
        user_id: Optional[str] = None
    ) -> PurchaseOrder:
        """
        Create a new Purchase Order with calculated tax, lines, and total amounts.
        """
        v_res = await db.execute(select(Vendor).where(Vendor.id == payload.vendor_id, Vendor.tenant_id == tenant_id))
        vendor = v_res.scalar_one_or_none()
        if not vendor:
            raise EntityNotFoundError("Vendor not found.")

        subtotal = Decimal("0.0")
        total_tax = Decimal("0.0")

        for line in payload.lines:
            subtotal += (line.quantity_ordered * line.unit_price)
            total_tax += line.tax_amount

        total_amount = subtotal + total_tax
        po_num = await cls.generate_po_number(db, tenant_id, payload.order_date)

        po = PurchaseOrder(
            tenant_id=tenant_id,
            po_number=po_num,
            vendor_id=payload.vendor_id,
            requisition_id=payload.requisition_id,
            order_date=payload.order_date,
            expected_delivery_date=payload.expected_delivery_date,
            payment_terms_days=payload.payment_terms_days,
            currency=payload.currency.upper(),
            exchange_rate=payload.exchange_rate,
            status=POStatus.DRAFT.value,
            shipping_address=payload.shipping_address,
            subtotal=subtotal,
            tax_amount=total_tax,
            total_amount=total_amount,
            notes=payload.notes
        )
        db.add(po)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            lt = (line.quantity_ordered * line.unit_price) + line.tax_amount
            po_line = PurchaseOrderLine(
                tenant_id=tenant_id,
                po_id=po.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity_ordered=line.quantity_ordered,
                quantity_received=Decimal("0.0"),
                quantity_billed=Decimal("0.0"),
                unit_price=line.unit_price,
                tax_rate_id=line.tax_rate_id,
                tax_amount=line.tax_amount,
                line_total=lt
            )
            db.add(po_line)

        await db.commit()
        await db.refresh(po)
        return po

    @classmethod
    async def approve_purchase_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        po_id: str,
        user_id: str
    ) -> PurchaseOrder:
        """
        Formally approve PO and transition to ISSUED status ready for receiving.
        """
        query = select(PurchaseOrder).where(
            PurchaseOrder.id == po_id,
            PurchaseOrder.tenant_id == tenant_id
        ).options(selectinload(PurchaseOrder.lines))
        res = await db.execute(query)
        po = res.scalar_one_or_none()

        if not po:
            raise EntityNotFoundError("Purchase order not found.")

        if po.status in [POStatus.APPROVED.value, POStatus.ISSUED.value]:
            raise BusinessRuleViolationError("PO is already approved.")

        po.status = POStatus.ISSUED.value
        po.approved_by_id = user_id
        po.approved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(po)

        # Publish event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_PO_APPROVED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"po_id": po.id, "po_number": po.po_number, "total_amount": float(po.total_amount)}
        ))

        return po
