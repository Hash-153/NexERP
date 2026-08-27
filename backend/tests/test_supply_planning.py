"""Supply planning calculation and inventory policy tests."""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.supply_planning.schemas import ForecastCreate, PolicyCreate, ScorecardCreate
from backend.src.modules.supply_planning.services import SupplyPlanningService


@pytest.mark.asyncio
async def test_replenishment_recommendation_respects_safety_stock_and_multiple(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    await SupplyPlanningService.upsert_policy(db_session, tenant_id, PolicyCreate(item_id="item-001", warehouse_id="wh-001", safety_stock_quantity=Decimal("20"), minimum_order_quantity=Decimal("10"), order_multiple=Decimal("10"), preferred_supplier_id="vendor-001"))
    recommendation = await SupplyPlanningService.recommend(db_session, tenant_id, "item-001", "wh-001", Decimal("35"), Decimal("50"), date(2026, 9, 1), Decimal("12.50"))
    assert recommendation.recommended_quantity == Decimal("40")
    assert recommendation.estimated_total_cost == Decimal("500.00")
    assert recommendation.priority == "NORMAL"


@pytest.mark.asyncio
async def test_recommendation_requires_active_policy(db_session: AsyncSession):
    with pytest.raises(Exception, match="policy"):
        await SupplyPlanningService.recommend(db_session, "org_corp_hq_001", "unknown-item", "unknown-warehouse", Decimal("0"), Decimal("10"), date(2026, 9, 1))


@pytest.mark.asyncio
async def test_forecast_period_and_supplier_scorecard(db_session: AsyncSession):
    forecast = await SupplyPlanningService.create_forecast(db_session, "org_corp_hq_001", ForecastCreate(item_id="item-002", period_start=date(2026, 9, 1), period_end=date(2026, 9, 30), forecast_quantity=Decimal("100"), confidence_percent=Decimal("85")))
    assert forecast.status == "OPEN"
    scorecard = await SupplyPlanningService.create_scorecard(db_session, "org_corp_hq_001", ScorecardCreate(supplier_id="vendor-002", period_start=date(2026, 1, 1), period_end=date(2026, 6, 30), order_count=10, on_time_count=9, received_quantity=Decimal("1000"), accepted_quantity=Decimal("980"), spend_amount=Decimal("25000")))
    assert scorecard.on_time_percent == Decimal("90.00")
    assert scorecard.quality_percent == Decimal("98.00")
    assert scorecard.composite_score == Decimal("94.00")
