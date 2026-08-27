"""Advanced CRM pipeline and revenue forecasting services."""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from backend.src.core.exceptions import EntityNotFoundError
from .crm_models import CRMActivity, ForecastSnapshot, Opportunity, PipelineStage
from .crm_schemas import ActivityCreate, OpportunityCreate, OpportunityUpdate


class CRMService:
    """Maintains opportunity state, activity history, and weighted forecasts."""

    @staticmethod
    async def get_opportunity(db: AsyncSession, tenant_id: str, opportunity_id: str) -> Opportunity:
        result = await db.execute(select(Opportunity).where(Opportunity.id == opportunity_id, Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False).options(selectinload(Opportunity.activities)))
        opportunity = result.scalar_one_or_none()
        if not opportunity:
            raise EntityNotFoundError("Opportunity not found")
        return opportunity

    @classmethod
    async def create_opportunity(cls, db: AsyncSession, tenant_id: str, payload: OpportunityCreate) -> Opportunity:
        result = await db.execute(select(Opportunity).where(Opportunity.tenant_id == tenant_id).order_by(Opportunity.opportunity_number.desc()).limit(1))
        latest = result.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(latest.opportunity_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                pass
        opportunity = Opportunity(tenant_id=tenant_id, opportunity_number=f"OPP-{date.today().year}-{sequence:05d}", status="OPEN", **payload.model_dump())
        db.add(opportunity)
        await db.commit()
        await db.refresh(opportunity)
        return opportunity

    @classmethod
    async def list_opportunities(cls, db: AsyncSession, tenant_id: str, stage_code: Optional[str] = None, owner_id: Optional[str] = None) -> List[Opportunity]:
        query = select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False).order_by(Opportunity.expected_close_date.asc().nullslast(), Opportunity.amount.desc())
        if stage_code:
            query = query.where(Opportunity.stage_code == stage_code)
        if owner_id:
            query = query.where(Opportunity.owner_id == owner_id)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def update_opportunity(cls, db: AsyncSession, tenant_id: str, opportunity_id: str, payload: OpportunityUpdate) -> Opportunity:
        opportunity = await cls.get_opportunity(db, tenant_id, opportunity_id)
        updates = payload.model_dump(exclude_unset=True)
        if updates.get("status") == "LOST" and not updates.get("loss_reason") and not opportunity.loss_reason:
            raise ValueError("A loss reason is required when marking an opportunity lost")
        for key, value in updates.items():
            setattr(opportunity, key, value)
        opportunity.last_contact_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(opportunity)
        return opportunity

    @classmethod
    async def add_activity(cls, db: AsyncSession, tenant_id: str, payload: ActivityCreate, user_id: str) -> CRMActivity:
        if payload.opportunity_id:
            await cls.get_opportunity(db, tenant_id, payload.opportunity_id)
        activity = CRMActivity(tenant_id=tenant_id, owner_id=payload.owner_id or user_id, **payload.model_dump(exclude={"owner_id"}))
        db.add(activity)
        if payload.opportunity_id:
            opportunity = await cls.get_opportunity(db, tenant_id, payload.opportunity_id)
            opportunity.last_contact_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(activity)
        return activity

    @classmethod
    async def forecast(cls, db: AsyncSession, tenant_id: str, period_start: date, period_end: date, owner_id: Optional[str] = None) -> ForecastSnapshot:
        query = select(Opportunity).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False, Opportunity.status == "OPEN", Opportunity.expected_close_date >= period_start, Opportunity.expected_close_date <= period_end)
        if owner_id:
            query = query.where(Opportunity.owner_id == owner_id)
        opportunities = list((await db.execute(query)).scalars().all())
        pipeline = sum((item.amount for item in opportunities), Decimal("0"))
        weighted = sum((item.amount * Decimal(item.probability_percent) / Decimal("100") for item in opportunities), Decimal("0"))
        committed = sum((item.amount for item in opportunities if item.stage_code in {"COMMIT", "CLOSED_WON"}), Decimal("0"))
        best_case = sum((item.amount for item in opportunities if item.probability_percent >= 50), Decimal("0"))
        snapshot = ForecastSnapshot(tenant_id=tenant_id, snapshot_date=date.today(), period_start=period_start, period_end=period_end, owner_id=owner_id, pipeline_amount=pipeline, weighted_amount=weighted, committed_amount=committed, best_case_amount=best_case, opportunity_count=len(opportunities), status="FINAL")
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)
        return snapshot

    @classmethod
    async def stage_summary(cls, db: AsyncSession, tenant_id: str) -> List[dict]:
        result = await db.execute(select(Opportunity.stage_code, func.count(Opportunity.id), func.coalesce(func.sum(Opportunity.amount), 0), func.coalesce(func.avg(Opportunity.probability_percent), 0)).where(Opportunity.tenant_id == tenant_id, Opportunity.is_deleted == False, Opportunity.status == "OPEN").group_by(Opportunity.stage_code))
        return [{"stage_code": stage, "opportunity_count": count, "pipeline_amount": amount, "average_probability_percent": round(float(probability), 2)} for stage, count, amount, probability in result.all()]
