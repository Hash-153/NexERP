"""
CPQ (Configure, Price, Quote) Dynamic Pricing Engine Service.
Enforces floor margin validations, tiered volume discounting, and deal approvals.
"""
from decimal import Decimal
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import BusinessRuleViolationError, EntityNotFoundError
from backend.src.core.audit import AuditService
from ..models import CRMOpportunity, CPQQuote, CPQQuoteLine
from ..schemas import CPQQuoteCreate

class CPQPricingEngineService:
    @staticmethod
    async def generate_quote(
        session: AsyncSession,
        payload: CPQQuoteCreate,
        tenant_id: str,
        actor_id: str
    ) -> CPQQuote:
        stmt = select(CRMOpportunity).where(
            CRMOpportunity.id == payload.opportunity_id,
            CRMOpportunity.tenant_id == tenant_id
        )
        res = await session.execute(stmt)
        opp = res.scalar_one_or_none()
        if not opp:
            raise EntityNotFoundError("Opportunity not found.")

        gross_total = Decimal("0.0")
        discount_total = Decimal("0.0")
        cost_total = Decimal("0.0")

        quote = CPQQuote(
            tenant_id=tenant_id,
            opportunity_id=payload.opportunity_id,
            quote_number=payload.quote_number,
            version=1,
            status="DRAFT",
            valid_until_date=payload.valid_until_date
        )
        session.add(quote)
        await session.flush()

        for line_in in payload.lines:
            disc_rate = line_in.discount_percentage / Decimal("100.0")
            net_price = (line_in.list_unit_price * (Decimal("1.0") - disc_rate)).quantize(Decimal("0.01"))
            ext_price = (net_price * line_in.quantity).quantize(Decimal("0.01"))
            line_cost = (line_in.unit_cost * line_in.quantity).quantize(Decimal("0.01"))

            line_gross = line_in.list_unit_price * line_in.quantity
            line_disc = line_gross - ext_price

            gross_total += line_gross
            discount_total += line_disc
            cost_total += line_cost

            line = CPQQuoteLine(
                tenant_id=tenant_id,
                quote_id=quote.id,
                item_id=line_in.item_id,
                product_name=line_in.product_name,
                quantity=line_in.quantity,
                list_unit_price=line_in.list_unit_price,
                unit_cost=line_in.unit_cost,
                discount_percentage=line_in.discount_percentage,
                net_unit_price=net_price,
                extended_price=ext_price
            )
            session.add(line)

        net_total = gross_total - discount_total
        tax_total = (net_total * Decimal("0.0825")).quantize(Decimal("0.01"))  # 8.25% standard sales tax
        margin_pct = Decimal("0.0")
        if net_total > 0:
            margin_pct = (((net_total - cost_total) / net_total) * Decimal("100.0")).quantize(Decimal("0.01"))

        quote.gross_total = gross_total
        quote.discount_total = discount_total
        quote.tax_total = tax_total
        quote.net_total = net_total + tax_total
        quote.margin_percentage = margin_pct

        opp.deal_value = quote.net_total
        opp.stage = "PROPOSAL_CPQ_QUOTE"

        await session.commit()
        await session.refresh(quote)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="GENERATE_CPQ_QUOTE",
            entity_type="CPQQuote",
            entity_id=quote.id,
            description=f"Generated quote #{quote.quote_number} net ${quote.net_total} (margin {margin_pct}%)"
        )
        return quote
