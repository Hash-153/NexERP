"""Field service scheduling and customer experience tests."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.service_management.field_models import ServiceTechnician
from backend.src.modules.service_management.field_schemas import DispatchCreate, FeedbackCreate, MaintenancePlanCreate, TechnicianCreate
from backend.src.modules.service_management.field_services import CustomerExperienceService, FieldService, KnowledgeService, PreventiveMaintenanceService
from backend.src.modules.service_management.schemas import TicketCreate, TicketStatusUpdate
from backend.src.modules.service_management.services import ServiceManagementService


@pytest.mark.asyncio
async def test_dispatch_conflict_and_lifecycle(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(subject="Chiller alarm", description="The chiller alarm is active and production temperature is rising."))
    technician = await FieldService.create_technician(db_session, tenant_id, TechnicianCreate(technician_code="TECH-01", display_name="Morgan Lee", territory="North"))
    start = datetime(2026, 4, 1, 8, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    first = await FieldService.create_dispatch(db_session, tenant_id, DispatchCreate(ticket_id=ticket.id, technician_id=technician.id, scheduled_start=start, scheduled_end=end, address="Plant 1"))
    with pytest.raises(ValueError, match="already has"):
        await FieldService.create_dispatch(db_session, tenant_id, DispatchCreate(ticket_id=ticket.id, technician_id=technician.id, scheduled_start=start + timedelta(minutes=30), scheduled_end=end + timedelta(hours=1)))
    assert first.dispatch_number.startswith("DSP-2026-")


@pytest.mark.asyncio
async def test_maintenance_rolls_forward_and_feedback_requires_resolution(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    plan = await PreventiveMaintenanceService.create_plan(db_session, tenant_id, MaintenancePlanCreate(asset_id="asset-001", plan_number="PM-001", name="Quarterly inspection", frequency_days=90, next_due_date=date(2026, 1, 1)))
    completed = await PreventiveMaintenanceService.complete_plan(db_session, tenant_id, plan.id, date(2026, 2, 15))
    assert completed.next_due_date == date(2026, 5, 16)
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(subject="Replace filter", description="The air filter needs replacement during the scheduled visit."))
    with pytest.raises(ValueError, match="resolved"):
        await CustomerExperienceService.submit_feedback(db_session, tenant_id, FeedbackCreate(ticket_id=ticket.id, rating=5))
    await ServiceManagementService.update_ticket_status(db_session, tenant_id, ticket.id, TicketStatusUpdate(status="IN_PROGRESS"))
    await ServiceManagementService.update_ticket_status(db_session, tenant_id, ticket.id, TicketStatusUpdate(status="RESOLVED"))
    feedback = await CustomerExperienceService.submit_feedback(db_session, tenant_id, FeedbackCreate(ticket_id=ticket.id, rating=5, resolution_rating=4))
    assert feedback.rating == 5


@pytest.mark.asyncio
async def test_published_knowledge_search_increments_views(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    article = await KnowledgeService.create_article(db_session, tenant_id, __import__("backend.src.modules.service_management.field_schemas", fromlist=["ArticleCreate"]).ArticleCreate(article_number="KB-001", title="Reset a chiller alarm", body="Open the controller panel, acknowledge the alarm, and verify the return temperature."))
    await KnowledgeService.publish(db_session, tenant_id, article.id)
    results = await KnowledgeService.search(db_session, tenant_id, "chiller")
    assert len(results) == 1
    assert results[0].view_count == 1
