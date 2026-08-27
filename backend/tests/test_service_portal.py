"""Customer portal security and appointment workflow tests."""

from datetime import date, datetime, timedelta, timezone
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.service_management.portal_schemas import AppointmentRequestCreate, AppointmentReview, ConversationCreate
from backend.src.modules.service_management.portal_services import CustomerPortalService
from backend.src.modules.service_management.schemas import TicketCreate
from backend.src.modules.service_management.services import ServiceManagementService


@pytest.mark.asyncio
async def test_portal_token_is_hashed_and_validated(db_session: AsyncSession):
    raw, record = await CustomerPortalService.issue_token(db_session, "org_corp_hq_001", "customer-001", days=7)
    assert raw not in record.token_hash
    assert len(record.token_hash) == 64
    validated = await CustomerPortalService.validate_token(db_session, "org_corp_hq_001", raw)
    assert validated.id == record.id
    with pytest.raises(ValueError, match="invalid"):
        await CustomerPortalService.validate_token(db_session, "org_other", raw)


@pytest.mark.asyncio
async def test_portal_appointment_and_messages_are_customer_scoped(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(customer_id="customer-001", subject="Dock door repair", description="The dock door will not close and needs a field visit."))
    request = await CustomerPortalService.request_appointment(db_session, tenant_id, AppointmentRequestCreate(ticket_id=ticket.id, customer_id="customer-001", preferred_start=datetime(2026, 6, 1, 9, tzinfo=timezone.utc), preferred_end=datetime(2026, 6, 1, 11, tzinfo=timezone.utc), contact_name="Jamie Customer"))
    reviewed = await CustomerPortalService.review_appointment(db_session, tenant_id, request.id, AppointmentReview(status="CONFIRMED", review_notes="Technician reserved"), "usr_admin_001")
    assert reviewed.status == "CONFIRMED"
    message = await CustomerPortalService.add_message(db_session, tenant_id, ConversationCreate(ticket_id=ticket.id, customer_id="customer-001", message="The loading area is accessible from the east gate."), "CUSTOMER")
    assert message.is_internal is False
    messages = await CustomerPortalService.list_messages(db_session, tenant_id, ticket.id)
    assert len(messages) == 1
    with pytest.raises(ValueError, match="another"):
        await CustomerPortalService.add_message(db_session, tenant_id, ConversationCreate(ticket_id=ticket.id, customer_id="customer-999", message="Unauthorized message"), "CUSTOMER")
