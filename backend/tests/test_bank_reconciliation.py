"""
NexERP Bank Statement Matching & Reconciliation Test Suite.
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.modules.financials.models import Account, FiscalYear
from backend.src.modules.financials.services import (
    BankReconciliationService,
    FiscalPeriodService,
    GeneralLedgerService
)
from backend.src.modules.financials.schemas import FiscalYearCreate, JournalEntryCreate, JournalEntryLineCreate


@pytest.mark.asyncio
async def test_bank_statement_line_matching_rules(db_session: AsyncSession):
    """
    Verify automatic statement matching with exact amount/reference and date tolerance.
    """
    tenant_id = "org_corp_hq_001"

    bank_acc = Account(tenant_id=tenant_id, code="10100", name="Chase Bank", account_type="ASSET", classification="CASH_AND_BANK", currency="USD", current_balance=Decimal("0.0"))
    rev_acc = Account(tenant_id=tenant_id, code="40100", name="Revenue", account_type="REVENUE", classification="OPERATING_REVENUE", currency="USD", current_balance=Decimal("0.0"))
    db_session.add_all([bank_acc, rev_acc])
    await db_session.flush()

    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )
    period = fy.periods[0]

    # Post Deposit in GL: $5,000 with Reference 'CUST-WIRE-8891' on Jan 10
    jv_payload = JournalEntryCreate(
        entry_date=date(2026, 1, 10),
        period_id=period.id,
        currency="USD",
        reference="CUST-WIRE-8891",
        narration="Customer Wire Receipt",
        lines=[
            JournalEntryLineCreate(account_id=bank_acc.id, debit=Decimal("5000.00"), credit=Decimal("0.0"), description="Incoming wire payment"),
            JournalEntryLineCreate(account_id=rev_acc.id, debit=Decimal("0.0"), credit=Decimal("5000.00"), description="Sales recognition"),
        ]
    )
    jv = await GeneralLedgerService.create_journal_entry(db_session, tenant_id, jv_payload)
    await GeneralLedgerService.post_journal_entry(db_session, tenant_id, jv.id, "tester")

    # Imported statement lines from bank
    statement_lines = [
        {"date": "2026-01-10", "amount": 5000.00, "reference": "CUST-WIRE-8891"},
        {"date": "2026-01-15", "amount": 250.00, "reference": "BANK-SERVICE-FEE"},
    ]

    result = await BankReconciliationService.match_statement_lines_with_gl(
        db=db_session,
        tenant_id=tenant_id,
        bank_account_id=bank_acc.id,
        statement_lines=statement_lines
    )

    assert result["matched_count"] == 1
    assert result["unmatched_statement_count"] == 1
    assert result["matches"][0]["match_type"] == "EXACT_AMOUNT_AND_REFERENCE"
