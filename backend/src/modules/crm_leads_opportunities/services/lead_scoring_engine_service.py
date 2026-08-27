"""
Predictive Lead Scoring & Routing Service.
"""
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.audit import AuditService
from ..models import CRMLead
from ..schemas import CRMLeadCreate

class LeadScoringEngineService:
    @staticmethod
    def calculate_score(lead_source: str, budget: Decimal, timeframe: int) -> int:
        score = 40  # base
        if lead_source in ("PARTNER_REFERRAL", "INBOUND_API"):
            score += 25
        elif lead_source == "ORGANIC_WEB":
            score += 15
        
        if budget and budget > Decimal("50000.00"):
            score += 20
        elif budget and budget > Decimal("10000.00"):
            score += 10
            
        if timeframe <= 1:
            score += 15
        elif timeframe <= 3:
            score += 5
            
        return min(100, score)

    @staticmethod
    async def create_and_score_lead(
        session: AsyncSession,
        payload: CRMLeadCreate,
        tenant_id: str,
        actor_id: str
    ) -> CRMLead:
        score = LeadScoringEngineService.calculate_score(
            payload.lead_source,
            payload.budget_amount or Decimal("0.0"),
            payload.decision_timeframe_months
        )

        status = "SALES_QUALIFIED" if score >= 75 else ("MARKETING_QUALIFIED" if score >= 50 else "NEW_UNTOUCHED")

        lead = CRMLead(
            tenant_id=tenant_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            company_name=payload.company_name,
            job_title=payload.job_title,
            lead_source=payload.lead_source,
            qualification_status=status,
            predictive_score=score,
            budget_amount=payload.budget_amount,
            decision_timeframe_months=payload.decision_timeframe_months,
            assigned_sales_rep_id=actor_id,
            notes=payload.notes
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)

        await AuditService.log_action(
            session=session,
            tenant_id=tenant_id,
            actor_id=actor_id,
            action="CREATE_LEAD",
            entity_type="CRMLead",
            entity_id=lead.id,
            description=f"Created and scored lead {lead.email} at {score}/100"
        )
        return lead
