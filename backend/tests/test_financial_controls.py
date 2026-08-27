"""Financial close and control workflow tests."""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.modules.financial_controls.schemas import ApprovalDecision, ApprovalPolicyCreate, ApprovalRequestCreate, CashForecastCreate, ChecklistComplete, CloseChecklistCreate, ReconciliationExceptionCreate, ReconciliationResolution
from backend.src.modules.financial_controls.services import FinancialControlService
from backend.src.modules.financials.models import FiscalPeriod, FiscalYear


@pytest.mark.asyncio
async def test_period_close_is_blocked_until_required_controls_complete(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    year = FiscalYear(tenant_id=tenant_id, name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    db_session.add(year)
    await db_session.flush()
    period = FiscalPeriod(tenant_id=tenant_id, fiscal_year_id=year.id, period_number=1, name="January 2026", start_date=date(2026, 1, 1), end_date=date(2026, 1, 31))
    db_session.add(period)
    await db_session.commit()
    item = await FinancialControlService.add_checklist_item(db_session, tenant_id, CloseChecklistCreate(period_id=period.id, checklist_code="BANK-REC", title="Complete bank reconciliation"))
    with pytest.raises(Exception, match="required close controls"):
        await FinancialControlService.lock_period(db_session, tenant_id, period.id)
    await FinancialControlService.complete_checklist_item(db_session, tenant_id, item.id, ChecklistComplete(evidence_reference="REC-2026-01"), "usr_admin_001")
    locked = await FinancialControlService.lock_period(db_session, tenant_id, period.id)
    assert locked.is_locked is True


@pytest.mark.asyncio
async def test_approval_policy_cash_summary_and_reconciliation(db_session: AsyncSession):
    tenant_id = "org_corp_hq_001"
    await FinancialControlService.create_policy(db_session, tenant_id, ApprovalPolicyCreate(document_type="PURCHASE_ORDER", policy_code="PO-10K", name="Purchase approval", minimum_amount=Decimal("1000"), maximum_amount=Decimal("10000"), required_role="FinanceManager"))
    request = await FinancialControlService.request_approval(db_session, tenant_id, ApprovalRequestCreate(document_type="PURCHASE_ORDER", document_id="po-001", amount=Decimal("5000")), "usr_admin_001")
    assert request.status == "PENDING"
    approved = await FinancialControlService.decide_approval(db_session, tenant_id, request.id, ApprovalDecision(status="APPROVED", decision_note="Reviewed"), "usr_admin_001")
    assert approved.status == "APPROVED"
    await FinancialControlService.add_cash_line(db_session, tenant_id, CashForecastCreate(period_start=date(2026, 2, 1), period_end=date(2026, 2, 28), forecast_type="INFLOW", category="AR", description="Expected customer receipts", expected_amount=Decimal("10000"), probability_percent=Decimal("80")))
    await FinancialControlService.add_cash_line(db_session, tenant_id, CashForecastCreate(period_start=date(2026, 2, 1), period_end=date(2026, 2, 28), forecast_type="OUTFLOW", category="AP", description="Supplier settlements", expected_amount=Decimal("3000")))
    summary = await FinancialControlService.cash_summary(db_session, tenant_id)
    assert summary["weighted_net_cash"] == Decimal("5000")
    exception = await FinancialControlService.create_reconciliation_exception(db_session, tenant_id, ReconciliationExceptionCreate(statement_reference="BANK-01", transaction_date=date(2026, 2, 4), book_amount=Decimal("100"), statement_amount=Decimal("125"), exception_type="AMOUNT_MISMATCH", description="Bank fee missing from books"))
    assert exception.variance_amount == Decimal("25")
    resolved = await FinancialControlService.resolve_reconciliation_exception(db_session, tenant_id, exception.id, ReconciliationResolution(resolution_note="Posted bank fee journal"), "usr_admin_001")
    assert resolved.status == "RESOLVED"
