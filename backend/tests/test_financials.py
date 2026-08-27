"""
NexERP Financials & General Ledger Automated Test Suite.
Tests Double-Entry GAAP/IFRS Invariants, Period Controls, and Running Balance Integrity.
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import UnbalancedJournalEntryError, AccountingPeriodClosedError
from backend.src.modules.financials.models import Account, FiscalYear, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService, FiscalPeriodService, FinancialReportingService
from backend.src.modules.financials.schemas import (
    FiscalYearCreate,
    JournalEntryCreate,
    JournalEntryLineCreate
)


@pytest.mark.asyncio
async def test_unbalanced_journal_entry_rejection(db_session: AsyncSession):
    """
    Ensure the GL engine rejects unbalanced journal entries (Debits != Credits).
    """
    tenant_id = "org_corp_hq_001"

    # 1. Setup Accounts
    cash_acc = Account(tenant_id=tenant_id, code="10100", name="Cash", account_type="ASSET", classification="CASH_AND_BANK")
    rev_acc = Account(tenant_id=tenant_id, code="40100", name="Sales", account_type="REVENUE", classification="OPERATING_REVENUE")
    db_session.add_all([cash_acc, rev_acc])
    await db_session.flush()

    # 2. Setup Period
    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )
    period = fy.periods[0]

    # 3. Create Unbalanced Entry ($1,000 Debit vs $800 Credit)
    unbalanced_payload = JournalEntryCreate(
        entry_date=date(2026, 1, 15),
        period_id=period.id,
        reference="UNBAL-001",
        narration="Faulty Entry",
        lines=[
            JournalEntryLineCreate(account_id=cash_acc.id, debit=Decimal("1000.00"), credit=Decimal("0.0")),
            JournalEntryLineCreate(account_id=rev_acc.id, debit=Decimal("0.0"), credit=Decimal("800.00")),
        ]
    )

    with pytest.raises(UnbalancedJournalEntryError):
        await GeneralLedgerService.create_journal_entry(db_session, tenant_id, unbalanced_payload)


@pytest.mark.asyncio
async def test_balanced_journal_posting_and_running_balances(db_session: AsyncSession):
    """
    Ensure balanced entries post successfully and update account balances correctly.
    """
    tenant_id = "org_corp_hq_001"

    cash_acc = Account(tenant_id=tenant_id, code="10100", name="Operating Bank", account_type="ASSET", classification="CASH_AND_BANK")
    capital_acc = Account(tenant_id=tenant_id, code="30100", name="Share Capital", account_type="EQUITY", classification="SHARE_CAPITAL")
    db_session.add_all([cash_acc, capital_acc])
    await db_session.flush()

    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )
    period = fy.periods[0]

    balanced_payload = JournalEntryCreate(
        entry_date=date(2026, 1, 1),
        period_id=period.id,
        reference="JV-2026-001",
        narration="Owner investment",
        lines=[
            JournalEntryLineCreate(account_id=cash_acc.id, debit=Decimal("50000.00"), credit=Decimal("0.0")),
            JournalEntryLineCreate(account_id=capital_acc.id, debit=Decimal("0.0"), credit=Decimal("50000.00")),
        ]
    )

    jv = await GeneralLedgerService.create_journal_entry(db_session, tenant_id, balanced_payload)
    assert jv.status == "DRAFT"

    posted_jv = await GeneralLedgerService.post_journal_entry(db_session, tenant_id, jv.id, "test_user")
    assert posted_jv.status == "POSTED"

    # Verify Account running balances
    await db_session.refresh(cash_acc)
    await db_session.refresh(capital_acc)

    assert cash_acc.current_balance == Decimal("50000.00")
    assert capital_acc.current_balance == Decimal("50000.00")

    # Verify Trial Balance
    tb = await FinancialReportingService.generate_trial_balance(db_session, tenant_id, date(2026, 1, 31))
    assert tb.total_debits == Decimal("50000.00")
    assert tb.total_credits == Decimal("50000.00")
    assert tb.is_balanced is True


@pytest.mark.asyncio
async def test_closed_fiscal_period_blocking(db_session: AsyncSession):
    """
    Ensure posting to a locked fiscal period is rejected.
    """
    tenant_id = "org_corp_hq_001"

    cash_acc = Account(tenant_id=tenant_id, code="10100", name="Cash", account_type="ASSET", classification="CASH_AND_BANK")
    rev_acc = Account(tenant_id=tenant_id, code="40100", name="Sales", account_type="REVENUE", classification="OPERATING_REVENUE")
    db_session.add_all([cash_acc, rev_acc])
    await db_session.flush()

    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )
    period = fy.periods[0]

    # Lock period
    await FiscalPeriodService.lock_period(db_session, tenant_id, period.id)

    payload = JournalEntryCreate(
        entry_date=date(2026, 1, 15),
        period_id=period.id,
        reference="JV-CLOSED",
        narration="Attempt in closed period",
        lines=[
            JournalEntryLineCreate(account_id=cash_acc.id, debit=Decimal("100.00"), credit=Decimal("0.0")),
            JournalEntryLineCreate(account_id=rev_acc.id, debit=Decimal("0.0"), credit=Decimal("100.00")),
        ]
    )

    with pytest.raises(AccountingPeriodClosedError):
        await GeneralLedgerService.create_journal_entry(db_session, tenant_id, payload)
