"""Service billing and SLA escalation invariants."""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.service_management.billing_schemas import ChargeCreate, ChargeStatusUpdate, InvoiceBatchCreate
from backend.src.modules.service_management.billing_services import SLAEscalationService, ServiceBillingService
from backend.src.modules.service_management.schemas import ContractCreate, TicketCreate
from backend.src.modules.service_management.services import ServiceManagementService


@pytest.mark.asyncio
async def test_charge_rounding_and_invoice_batching(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(customer_id="customer-001", subject="Calibration visit", description="The line sensor requires an annual calibration visit."))
    charge = await ServiceBillingService.create_charge(db_session, tenant_id, ChargeCreate(ticket_id=ticket.id, charge_date=date(2026, 5, 1), charge_type="LABOR", description="Calibration labor", quantity=Decimal("2.5"), unit_price=Decimal("100.00"), discount_percent=Decimal("10"), tax_percent=Decimal("8.25")))
    assert charge.net_amount == Decimal("225.00")
    assert charge.tax_amount == Decimal("18.56")
    assert charge.total_amount == Decimal("243.56")
    await ServiceBillingService.update_charge_status(db_session, tenant_id, charge.id, ChargeStatusUpdate(status="APPROVED"))
    batch = await ServiceBillingService.create_batch(db_session, tenant_id, InvoiceBatchCreate(customer_id="customer-001", period_start=date(2026, 5, 1), period_end=date(2026, 5, 31)), "usr_admin_001")
    assert batch.charge_count == 1
    assert batch.total_amount == Decimal("243.56")
    refreshed = await ServiceBillingService.list_charges(db_session, tenant_id, ticket_id=ticket.id)
    assert refreshed[0].status == "INVOICED"


@pytest.mark.asyncio
async def test_sla_escalation_is_deduplicated(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    contract = await ServiceManagementService.create_contract(db_session, tenant_id, ContractCreate(contract_number="SLA-ESC", name="Escalation SLA", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), response_hours=Decimal("1")))
    ticket = await ServiceManagementService.create_ticket(db_session, tenant_id, TicketCreate(contract_id=contract.id, subject="Urgent line stop", description="Production has stopped and immediate support is required.", priority="URGENT"))
    ticket.opened_at = ticket.opened_at.replace(year=2025)
    await db_session.commit()
    first = await SLAEscalationService.detect(db_session, tenant_id)
    second = await SLAEscalationService.detect(db_session, tenant_id)
    assert len(first) == 1
    assert second == []
