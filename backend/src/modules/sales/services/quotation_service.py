"""
NexERP Sales Quotation Service.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.sales.models import SalesQuotation, SalesQuotationLine
from backend.src.modules.sales.schemas import SalesQuotationCreate
from backend.src.modules.sales.enums import QuoteStatus
from backend.src.modules.accounts_receivable.models import Customer


class QuotationService:
    """
    Sales quotation proposal generation service.
    """

    @classmethod
    async def generate_quote_number(cls, db: AsyncSession, tenant_id: str, quote_date: date) -> str:
        year_str = str(quote_date.year)
        prefix = f"QT-{year_str}-"
        query = select(SalesQuotation).where(SalesQuotation.tenant_id == tenant_id).order_by(SalesQuotation.quote_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.quote_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_quotation(cls, db: AsyncSession, tenant_id: str, payload: SalesQuotationCreate) -> SalesQuotation:
        cust_res = await db.execute(select(Customer).where(Customer.id == payload.customer_id, Customer.tenant_id == tenant_id))
        cust = cust_res.scalar_one_or_none()
        if not cust:
            raise EntityNotFoundError("Customer not found.")

        subtotal = Decimal("0.0")
        total_discount = Decimal("0.0")
        total_tax = Decimal("0.0")

        for line in payload.lines:
            gross = line.quantity * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            subtotal += (gross - disc)
            total_discount += disc
            total_tax += line.tax_amount

        total_amount = subtotal + total_tax
        quote_num = await cls.generate_quote_number(db, tenant_id, payload.quote_date)

        quote = SalesQuotation(
            tenant_id=tenant_id,
            quote_number=quote_num,
            customer_id=payload.customer_id,
            lead_id=payload.lead_id,
            quote_date=payload.quote_date,
            expiry_date=payload.expiry_date,
            status=QuoteStatus.DRAFT.value,
            currency=payload.currency.upper(),
            subtotal=subtotal,
            discount_amount=total_discount,
            tax_amount=total_tax,
            total_amount=total_amount,
            terms_and_conditions=payload.terms_and_conditions
        )
        db.add(quote)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            gross = line.quantity * line.unit_price
            disc = gross * (line.discount_percent / Decimal("100.0"))
            lt = (gross - disc) + line.tax_amount

            q_line = SalesQuotationLine(
                tenant_id=tenant_id,
                quotation_id=quote.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity=line.quantity,
                unit_price=line.unit_price,
                discount_percent=line.discount_percent,
                tax_amount=line.tax_amount,
                line_total=lt
            )
            db.add(q_line)

        await db.commit()
        await db.refresh(quote)
        return quote
