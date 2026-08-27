"""Demand forecasting and replenishment decision services."""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_UP
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .models import DemandForecast, PurchaseRecommendation, ReplenishmentPolicy, ShipmentMilestone, SupplierScorecard
from .schemas import ForecastCreate, MilestoneCreate, PolicyCreate, ScorecardCreate


class SupplyPlanningService:
    """Converts demand signals into explainable purchase recommendations."""

    @classmethod
    async def create_forecast(cls, db: AsyncSession, tenant_id: str, payload: ForecastCreate) -> DemandForecast:
        forecast = DemandForecast(tenant_id=tenant_id, status="OPEN", **payload.model_dump())
        db.add(forecast)
        await db.commit()
        await db.refresh(forecast)
        return forecast

    @classmethod
    async def upsert_policy(cls, db: AsyncSession, tenant_id: str, payload: PolicyCreate) -> ReplenishmentPolicy:
        result = await db.execute(select(ReplenishmentPolicy).where(ReplenishmentPolicy.tenant_id == tenant_id, ReplenishmentPolicy.item_id == payload.item_id, ReplenishmentPolicy.warehouse_id == payload.warehouse_id))
        policy = result.scalar_one_or_none()
        if policy:
            for key, value in payload.model_dump().items():
                setattr(policy, key, value)
        else:
            policy = ReplenishmentPolicy(tenant_id=tenant_id, active=True, **payload.model_dump())
            db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @classmethod
    async def recommend(cls, db: AsyncSession, tenant_id: str, item_id: str, warehouse_id: str, available_quantity: Decimal, demand_quantity: Decimal, required_date: date, estimated_unit_cost: Decimal = Decimal("0")) -> PurchaseRecommendation:
        result = await db.execute(select(ReplenishmentPolicy).where(ReplenishmentPolicy.tenant_id == tenant_id, ReplenishmentPolicy.item_id == item_id, ReplenishmentPolicy.warehouse_id == warehouse_id, ReplenishmentPolicy.active == True))
        policy = result.scalar_one_or_none()
        if not policy:
            raise EntityNotFoundError("Active replenishment policy not found")
        target = demand_quantity + policy.safety_stock_quantity
        shortfall = max(Decimal("0"), target - available_quantity)
        if shortfall == 0:
            raise ValueError("Available inventory covers demand and safety stock")
        multiple = policy.order_multiple
        quantity = (shortfall / multiple).quantize(Decimal("1"), rounding=ROUND_UP) * multiple
        quantity = max(quantity, policy.minimum_order_quantity)
        if policy.maximum_order_quantity:
            quantity = min(quantity, policy.maximum_order_quantity)
        result = await db.execute(select(PurchaseRecommendation).where(PurchaseRecommendation.tenant_id == tenant_id).order_by(PurchaseRecommendation.recommendation_number.desc()).limit(1))
        latest = result.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(latest.recommendation_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                pass
        recommendation = PurchaseRecommendation(tenant_id=tenant_id, recommendation_number=f"REC-{date.today().year}-{sequence:05d}", item_id=item_id, warehouse_id=warehouse_id, supplier_id=policy.preferred_supplier_id, required_date=required_date, demand_quantity=demand_quantity, available_quantity=available_quantity, safety_stock_quantity=policy.safety_stock_quantity, recommended_quantity=quantity, estimated_unit_cost=estimated_unit_cost, estimated_total_cost=quantity * estimated_unit_cost, reason="BELOW_REORDER_TARGET", priority="HIGH" if available_quantity <= policy.safety_stock_quantity else "NORMAL", status="PROPOSED")
        db.add(recommendation)
        await db.commit()
        await db.refresh(recommendation)
        return recommendation

    @classmethod
    async def list_recommendations(cls, db: AsyncSession, tenant_id: str, status: Optional[str] = None) -> List[PurchaseRecommendation]:
        query = select(PurchaseRecommendation).where(PurchaseRecommendation.tenant_id == tenant_id, PurchaseRecommendation.is_deleted == False).order_by(PurchaseRecommendation.required_date.asc())
        if status:
            query = query.where(PurchaseRecommendation.status == status)
        return list((await db.execute(query)).scalars().all())

    @classmethod
    async def create_scorecard(cls, db: AsyncSession, tenant_id: str, payload: ScorecardCreate) -> SupplierScorecard:
        on_time = Decimal(payload.on_time_count * 100) / Decimal(payload.order_count) if payload.order_count else Decimal("0")
        quality = Decimal(payload.accepted_quantity * 100) / Decimal(payload.received_quantity) if payload.received_quantity else Decimal("0")
        composite = (on_time * Decimal("0.5") + quality * Decimal("0.5")).quantize(Decimal("0.01"))
        scorecard = SupplierScorecard(tenant_id=tenant_id, on_time_percent=on_time.quantize(Decimal("0.01")), quality_percent=quality.quantize(Decimal("0.01")), composite_score=composite, status="FINAL", **payload.model_dump())
        db.add(scorecard)
        await db.commit()
        await db.refresh(scorecard)
        return scorecard

    @classmethod
    async def create_milestone(cls, db: AsyncSession, tenant_id: str, payload: MilestoneCreate) -> ShipmentMilestone:
        milestone = ShipmentMilestone(tenant_id=tenant_id, status="PLANNED", **payload.model_dump())
        db.add(milestone)
        await db.commit()
        await db.refresh(milestone)
        return milestone

    @classmethod
    async def complete_milestone(cls, db: AsyncSession, tenant_id: str, milestone_id: str, delay_reason: Optional[str] = None) -> ShipmentMilestone:
        result = await db.execute(select(ShipmentMilestone).where(ShipmentMilestone.id == milestone_id, ShipmentMilestone.tenant_id == tenant_id, ShipmentMilestone.is_deleted == False))
        milestone = result.scalar_one_or_none()
        if not milestone:
            raise EntityNotFoundError("Shipment milestone not found")
        milestone.status = "COMPLETED"
        milestone.actual_at = datetime.now(timezone.utc)
        milestone.delay_reason = delay_reason
        await db.commit()
        await db.refresh(milestone)
        return milestone
