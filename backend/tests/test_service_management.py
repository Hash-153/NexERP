"""Service management lifecycle and tenant-isolation tests."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.service_management.models import ServiceContract
from backend.src.modules.service_management.schemas import ActivityCreate, ContractCreate, TicketCreate, TicketStatusUpdate
from backend.src.modules.service_management.services import ServiceManagementService


@pytest.mark.asyncio
async def test_ticket_sla_and_activity_consumption(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    contract = await ServiceManagementService.create_contract(db_session, tenant_id, ContractCreate(contract_number="SLA-001", name="Gold support", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), included_hours=Decimal("100"), response_hours=Decimal("4")))
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(contract_id=contract.id, subject="Pump vibration", description="The production pump is vibrating above its normal level.", priority="HIGH"))
    assert ticket.ticket_number.startswith("TKT-2026-")
    assert ticket.due_at is not None
    assert (ticket.due_at - ticket.opened_at).total_seconds() == 4 * 3600
    await ServiceManagementService.update_ticket_status(db_session, tenant_id, ticket.id, TicketStatusUpdate(status="IN_PROGRESS"))
    activity = await ServiceManagementService.add_activity(db_session, tenant_id, ticket.id, ActivityCreate(started_at=datetime(2026, 2, 1, 8, tzinfo=timezone.utc), ended_at=datetime(2026, 2, 1, 10, 30, tzinfo=timezone.utc), description="Diagnosed bearing alignment"))
    assert activity.hours == Decimal("2.50")
    await db_session.refresh(contract)
    assert contract.consumed_hours == Decimal("2.50")


@pytest.mark.asyncio
async def test_invalid_ticket_transition_is_rejected(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(subject="Network outage", description="The warehouse network is unavailable for handheld scanners."))
    await ServiceManagementService.update_ticket_status(db_session, tenant_id, ticket.id, TicketStatusUpdate(status="CANCELLED"))
    with pytest.raises(ValueError, match="Cannot transition"):
        await ServiceManagementService.update_ticket_status(db_session, tenant_id, ticket.id, TicketStatusUpdate(status="IN_PROGRESS"))


@pytest.mark.asyncio
async def test_contract_end_date_validation():
    with pytest.raises(ValueError, match="end date"):
        ContractCreate(contract_number="BAD", name="Bad dates", start_date=date(2026, 2, 1), end_date=date(2026, 1, 1))
