"""CRM opportunity lifecycle and forecasting tests."""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.sales.crm_schemas import ActivityCreate, OpportunityCreate, OpportunityUpdate
from backend.src.modules.sales.crm_services import CRMService


@pytest.mark.asyncio
async def test_crm_opportunity_forecast_and_loss_controls(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    opportunity = await CRMService.create_opportunity(db_session, tenant_id, OpportunityCreate(name="Plant expansion", amount=Decimal("100000"), probability_percent=60, stage_code="COMMIT", expected_close_date=date(2026, 10, 15)))
    assert opportunity.opportunity_number.startswith("OPP-2026-")
    with pytest.raises(ValueError, match="loss reason"):
        await CRMService.update_opportunity(db_session, tenant_id, opportunity.id, OpportunityUpdate(status="LOST"))
    await CRMService.add_activity(db_session, tenant_id, ActivityCreate(opportunity_id=opportunity.id, activity_type="CALL", subject="Budget review", outcome="Customer requested revised timeline"), "usr_admin_001")
    forecast = await CRMService.forecast(db_session, tenant_id, date(2026, 10, 1), date(2026, 10, 31))
    assert forecast.pipeline_amount == Decimal("100000")
    assert forecast.weighted_amount == Decimal("60000")
    assert forecast.committed_amount == Decimal("100000")


@pytest.mark.asyncio
async def test_crm_activity_requires_a_parent():
    with pytest.raises(ValueError, match="requires an opportunity"):
        ActivityCreate(activity_type="NOTE", subject="Unlinked note")
