"""
NexERP Sales Order Processing & Inventory Allocation Engine.
Validates customer credit, confirms sales orders, and manages soft stock reservation allocations.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError, CreditLimitExceededError
from backend.src.modules.sales.models import SalesOrder, SalesOrderLine
from backend.src.modules.sales.schemas import SalesOrderCreate
from backend.src.modules.sales.enums import SalesOrderStatus
from backend.src.modules.accounts_receivable.models import Customer
from backend.src.modules.inventory.models import StockItemBalance


class SalesOrderService:
    """
    Sales Order confirmation and inventory reservation service.
    """

    @classmethod
    async def generate_so_number(cls, db: AsyncSession, tenant_id: str, order_date: date) -> str:
        year_str = str(order_date.year)
        prefix = f"SO-{year_str}-"
        query = select(SalesOrder).where(SalesOrder.tenant_id == tenant_id).order_by(SalesOrder.so_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.so_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_sales_order(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: SalesOrderCreate,
        user_id: Optional[str] = None
    ) -> SalesOrder:
        """
        Create and confirm sales order, check customer credit limit, and reserve inventory stock.
        """
        c_res = await db.execute(select(Customer).where(Customer.id == payload.customer_id, Customer.tenant_id == tenant_id))
        customer = c_res.scalar_one_or_none()
        if not customer:
            raise EntityNotFoundError("Customer not found.")

        if customer.credit_hold:
            raise CreditLimitExceededError("Customer account is on credit hold. Cannot create sales order.")

        subtotal = Decimal("0.0")
        total_discount = Decimal("0.0")
        total_tax = Decimal("0.0")

        for line in payload.lines:
            gross = line.quantity_ordered * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            subtotal += (gross - disc)
            total_discount += disc
            total_tax += line.tax_amount

        total_amount = subtotal + total_tax

        if (customer.current_balance + total_amount) > customer.credit_limit:
            raise CreditLimitExceededError(
                f"Order total (${total_amount}) exceeds approved credit limit headroom for {customer.name}."
            )

        so_num = await cls.generate_so_number(db, tenant_id, payload.order_date)

        so = SalesOrder(
            tenant_id=tenant_id,
            so_number=so_num,
            customer_id=payload.customer_id,
            quotation_id=payload.quotation_id,
            order_date=payload.order_date,
            requested_delivery_date=payload.requested_delivery_date,
            currency=payload.currency.upper(),
            exchange_rate=payload.exchange_rate,
            status=SalesOrderStatus.CONFIRMED.value,
            shipping_address=payload.shipping_address or customer.shipping_address,
            payment_terms_days=payload.payment_terms_days,
            subtotal=subtotal,
            discount_amount=total_discount,
            tax_amount=total_tax,
            total_amount=total_amount,
            notes=payload.notes
        )
        db.add(so)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            gross = line.quantity_ordered * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            lt = (gross - disc) + line.tax_amount

            so_line = SalesOrderLine(
                tenant_id=tenant_id,
                sales_order_id=so.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity_ordered=line.quantity_ordered,
                quantity_allocated=line.quantity_ordered,  # Soft reservation
                quantity_fulfilled=Decimal("0.0"),
                quantity_invoiced=Decimal("0.0"),
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                tax_rate_id=line.tax_rate_id,
                tax_amount=line.tax_amount,
                line_total=lt
            )
            db.add(so_line)

        await db.commit()
        await db.refresh(so)
        return so

    @classmethod
    async def list_sales_orders(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 50) -> List[SalesOrder]:
        query = (
            select(SalesOrder)
            .where(SalesOrder.tenant_id == tenant_id, SalesOrder.is_deleted == False)
            .options(selectinload(SalesOrder.lines))
            .order_by(SalesOrder.order_date.desc(), SalesOrder.so_number.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await db.execute(query)
        return list(res.scalars().all())
