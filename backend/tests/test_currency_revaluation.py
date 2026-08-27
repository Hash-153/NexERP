"""
NexERP Multi-Currency FX Revaluation Test Suite (ASC 830 / IAS 21).
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.modules.financials.models import Account, FiscalYear, FiscalPeriod
from backend.src.modules.financials.services import (
    CurrencyRevaluationService,
    FiscalPeriodService,
    GeneralLedgerService
)
from backend.src.modules.financials.schemas import FiscalYearCreate, JournalEntryCreate, JournalEntryLineCreate


@pytest.mark.asyncio
async def test_currency_spot_rate_resolution():
    """Verify spot rate conversion between EUR and USD."""
    rate_eur_usd = await CurrencyRevaluationService.get_exchange_rate("EUR", "USD", date(2026, 1, 31))
    assert rate_eur_usd == Decimal("1.085000")

    rate_usd_usd = await CurrencyRevaluationService.get_exchange_rate("USD", "USD", date(2026, 1, 31))
    assert rate_usd_usd == Decimal("1.000000")


@pytest.mark.asyncio
async def test_foreign_currency_account_unrealized_fx_calculation(db_session: AsyncSession):
    """
    Verify unrealized FX gain calculation when EUR bank account appreciates relative to USD base currency.
    """
    tenant_id = "org_corp_hq_001"

    # Setup EUR Bank Account & Capital
    eur_bank = Account(tenant_id=tenant_id, code="10150", name="EUR Euro Operating Account", account_type="ASSET", classification="CASH_AND_BANK", currency="EUR", current_balance=Decimal("0.0"))
    capital_acc = Account(tenant_id=tenant_id, code="30100", name="Paid-in Capital", account_type="EQUITY", classification="SHARE_CAPITAL", currency="USD", current_balance=Decimal("0.0"))
    fx_gain_acc = Account(tenant_id=tenant_id, code="40900", name="Unrealized FX Gain", account_type="REVENUE", classification="OPERATING_REVENUE", currency="USD", current_balance=Decimal("0.0"))
    fx_loss_acc = Account(tenant_id=tenant_id, code="60900", name="Unrealized FX Loss", account_type="EXPENSE", classification="GENERAL_AND_ADMIN", currency="USD", current_balance=Decimal("0.0"))
    db_session.add_all([eur_bank, capital_acc, fx_gain_acc, fx_loss_acc])
    await db_session.flush()

    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )
    period = fy.periods[0]

    # Initial Deposit of 10,000 EUR @ 1.05 rate = $10,500 USD book value
    jv_payload = JournalEntryCreate(
        entry_date=date(2026, 1, 5),
        period_id=period.id,
        currency="USD",
        exchange_rate=Decimal("1.0"),
        reference="EUR-DEPOSIT",
        narration="Initial EUR deposit",
        lines=[
            JournalEntryLineCreate(account_id=eur_bank.id, debit=Decimal("10500.00"), credit=Decimal("0.0"), debit_currency=Decimal("10000.00"), description="10,000 EUR @ 1.05", partner_type="BANK"),
            JournalEntryLineCreate(account_id=capital_acc.id, debit=Decimal("0.0"), credit=Decimal("10500.00"), debit_currency=Decimal("10500.00"), description="Equity contribution"),
        ]
    )
    jv = await GeneralLedgerService.create_journal_entry(db_session, tenant_id, jv_payload)
    await GeneralLedgerService.post_journal_entry(db_session, tenant_id, jv.id, "tester")

    # Month-end valuation rate is 1.10 (EUR appreciated). 10,000 EUR revalued = $11,000 USD (+ $500 Unrealized Gain)
    analysis = await CurrencyRevaluationService.calculate_account_unrealized_fx(
        db=db_session,
        tenant_id=tenant_id,
        account_id=eur_bank.id,
        valuation_date=date(2026, 1, 31),
        closing_rate=Decimal("1.100000"),
        base_currency="USD"
    )

    assert analysis["unrealized_fx_gain_loss"] == Decimal("500.00")
    assert analysis["is_gain"] is True
