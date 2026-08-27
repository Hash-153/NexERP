"""
NexERP Multi-Currency Revaluation and Foreign Exchange Accounting Engine.
Compliant with ASC 830 / IAS 21.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import (
    EntityNotFoundError,
    BusinessRuleViolationError,
    AccountingPeriodClosedError
)
from backend.src.modules.financials.models import (
    Account,
    FiscalPeriod,
    JournalEntry,
    JournalEntryLine
)
from backend.src.modules.financials.enums import AccountType, JournalStatus
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate
from backend.src.modules.financials.services.general_ledger_service import GeneralLedgerService


class CurrencyRevaluationService:
    """
    Automates month-end and year-end monetary balance revaluations across multi-currency
    bank accounts, AR sub-ledgers, and AP liabilities.
    """

    @classmethod
    async def get_exchange_rate(
        cls,
        from_currency: str,
        to_currency: str,
        effective_date: date,
        rates_table: Optional[Dict[Tuple[str, str], Decimal]] = None
    ) -> Decimal:
        if from_currency == to_currency:
            return Decimal("1.000000")

        if rates_table and (from_currency, to_currency) in rates_table:
            return rates_table[(from_currency, to_currency)]

        base_to_usd = {
            "USD": Decimal("1.000000"),
            "EUR": Decimal("1.085000"),
            "GBP": Decimal("1.272000"),
            "CAD": Decimal("0.735000"),
            "JPY": Decimal("0.006450"),
            "CHF": Decimal("1.123000"),
            "AUD": Decimal("0.658000"),
            "SGD": Decimal("0.742000"),
            "CNY": Decimal("0.138000"),
            "INR": Decimal("0.012050"),
            "MXN": Decimal("0.051200"),
            "BRL": Decimal("0.182000"),
        }

        usd_from = base_to_usd.get(from_currency, Decimal("1.000000"))
        usd_to = base_to_usd.get(to_currency, Decimal("1.000000"))

        if usd_to == Decimal("0.0"):
            return Decimal("1.000000")

        calculated_rate = (usd_from / usd_to).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        return calculated_rate

    @classmethod
    async def calculate_account_unrealized_fx(
        cls,
        db: AsyncSession,
        tenant_id: str,
        account_id: str,
        valuation_date: date,
        closing_rate: Decimal,
        base_currency: str = "USD"
    ) -> Dict:
        acc_res = await db.execute(
            select(Account).where(
                Account.id == account_id,
                Account.tenant_id == tenant_id,
                Account.is_deleted == False
            )
        )
        account = acc_res.scalar_one_or_none()
        if not account:
            raise EntityNotFoundError(f"Account ID '{account_id}' was not found.")

        lines_query = (
            select(JournalEntryLine)
            .join(JournalEntry)
            .where(
                JournalEntryLine.account_id == account_id,
                JournalEntryLine.tenant_id == tenant_id,
                JournalEntry.status == JournalStatus.POSTED.value,
                JournalEntry.entry_date <= valuation_date
            )
        )
        lines_res = await db.execute(lines_query)
        lines = lines_res.scalars().all()

        foreign_debit_sum = Decimal("0.0")
        foreign_credit_sum = Decimal("0.0")
        book_debit_sum = Decimal("0.0")
        book_credit_sum = Decimal("0.0")

        for line in lines:
            foreign_debit_sum += line.debit_currency if line.debit_currency is not None else line.debit
            foreign_credit_sum += line.credit_currency if line.credit_currency is not None else line.credit
            book_debit_sum += line.debit
            book_credit_sum += line.credit

        if account.account_type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
            foreign_balance = foreign_debit_sum - foreign_credit_sum
            book_balance = book_debit_sum - book_credit_sum
        else:
            foreign_balance = foreign_credit_sum - foreign_debit_sum
            book_balance = book_credit_sum - book_debit_sum

        revalued_balance = (foreign_balance * closing_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        unrealized_fx_variance = (revalued_balance - book_balance).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "account_id": account.id,
            "account_code": account.code,
            "account_name": account.name,
            "currency": account.currency,
            "foreign_currency_balance": foreign_balance,
            "book_value_base_currency": book_balance,
            "valuation_closing_rate": closing_rate,
            "revalued_balance_base_currency": revalued_balance,
            "unrealized_fx_gain_loss": unrealized_fx_variance,
            "is_gain": unrealized_fx_variance > Decimal("0.0") if account.account_type == AccountType.ASSET.value else unrealized_fx_variance < Decimal("0.0")
        }

    @classmethod
    async def execute_period_end_revaluation_run(
        cls,
        db: AsyncSession,
        tenant_id: str,
        period_id: str,
        valuation_date: date,
        unrealized_gain_account_id: str,
        unrealized_loss_account_id: str,
        exchange_rates: Dict[str, Decimal],
        base_currency: str = "USD",
        user_id: str = "system"
    ) -> JournalEntry:
        p_res = await db.execute(
            select(FiscalPeriod).where(
                FiscalPeriod.id == period_id,
                FiscalPeriod.tenant_id == tenant_id
            )
        )
        period = p_res.scalar_one_or_none()
        if not period:
            raise EntityNotFoundError("Fiscal period not found.")
        if period.is_locked:
            raise AccountingPeriodClosedError(f"Fiscal period '{period.name}' is closed.")

        accs_query = (
            select(Account)
            .where(
                Account.tenant_id == tenant_id,
                Account.currency != base_currency,
                Account.is_deleted == False,
                Account.account_type.in_([AccountType.ASSET.value, AccountType.LIABILITY.value])
            )
        )
        accs_res = await db.execute(accs_query)
        foreign_accounts = accs_res.scalars().all()

        reval_lines: List[JournalEntryLineCreate] = []

        for acc in foreign_accounts:
            rate = exchange_rates.get(acc.currency)
            if not rate:
                rate = await cls.get_exchange_rate(acc.currency, base_currency, valuation_date)

            analysis = await cls.calculate_account_unrealized_fx(
                db=db,
                tenant_id=tenant_id,
                account_id=acc.id,
                valuation_date=valuation_date,
                closing_rate=rate,
                base_currency=base_currency
            )

            variance = analysis["unrealized_fx_gain_loss"]
            if abs(variance) < Decimal("0.01"):
                continue

            if acc.account_type == AccountType.ASSET.value:
                if variance > Decimal("0.0"):
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=acc.id,
                        debit=variance,
                        credit=Decimal("0.0"),
                        description=f"FX Reval {acc.currency} @ {rate} (Gain)"
                    ))
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=unrealized_gain_account_id,
                        debit=Decimal("0.0"),
                        credit=variance,
                        description=f"Unrealized FX Gain on {acc.code} - {acc.name}"
                    ))
                else:
                    loss_amt = abs(variance)
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=unrealized_loss_account_id,
                        debit=loss_amt,
                        credit=Decimal("0.0"),
                        description=f"Unrealized FX Loss on {acc.code} - {acc.name}"
                    ))
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=acc.id,
                        debit=Decimal("0.0"),
                        credit=loss_amt,
                        description=f"FX Reval {acc.currency} @ {rate} (Loss)"
                    ))
            elif acc.account_type == AccountType.LIABILITY.value:
                if variance > Decimal("0.0"):
                    loss_amt = variance
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=unrealized_loss_account_id,
                        debit=loss_amt,
                        credit=Decimal("0.0"),
                        description=f"Unrealized FX Loss on Liability {acc.code}"
                    ))
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=acc.id,
                        debit=Decimal("0.0"),
                        credit=loss_amt,
                        description=f"FX Reval {acc.currency} @ {rate} (Liability Increase)"
                    ))
                else:
                    gain_amt = abs(variance)
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=acc.id,
                        debit=gain_amt,
                        credit=Decimal("0.0"),
                        description=f"FX Reval {acc.currency} @ {rate} (Liability Decrease)"
                    ))
                    reval_lines.append(JournalEntryLineCreate(
                        account_id=unrealized_gain_account_id,
                        debit=Decimal("0.0"),
                        credit=gain_amt,
                        description=f"Unrealized FX Gain on Liability {acc.code}"
                    ))

        if not reval_lines:
            raise BusinessRuleViolationError("No foreign currency balance variance detected requiring revaluation.")

        voucher_payload = JournalEntryCreate(
            entry_date=valuation_date,
            period_id=period.id,
            currency=base_currency,
            exchange_rate=Decimal("1.0"),
            reference=f"FX-REVAL-{valuation_date.strftime('%Y%m')}",
            narration=f"Month-end monetary balance FX revaluation for period {period.name}",
            source_document_type="CurrencyRevaluation",
            lines=reval_lines
        )

        journal = await GeneralLedgerService.create_journal_entry(db, tenant_id, voucher_payload, user_id)
        posted_journal = await GeneralLedgerService.post_journal_entry(db, tenant_id, journal.id, user_id)
        return posted_journal
