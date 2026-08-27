"""
NexERP Financial Statement & Reporting Engine.
Generates GAAP/IFRS compliant Trial Balance, Balance Sheet, and Income Statement (P&L).
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.modules.financials.models import Account, JournalEntry, JournalEntryLine
from backend.src.modules.financials.enums import AccountType, JournalStatus
from backend.src.modules.financials.schemas import (
    TrialBalanceResponse,
    TrialBalanceItem,
    BalanceSheetResponse,
    BalanceSheetSection,
    IncomeStatementResponse
)


class FinancialReportingService:
    """
    Financial statement calculation engine aggregating journal line postings.
    """

    @classmethod
    async def generate_trial_balance(
        cls,
        db: AsyncSession,
        tenant_id: str,
        as_of_date: date
    ) -> TrialBalanceResponse:
        """
        Generate General Ledger Trial Balance ensuring total debits equal total credits.
        """
        # Fetch all accounts
        acc_query = (
            select(Account)
            .where(
                Account.tenant_id == tenant_id,
                Account.is_deleted == False,
                Account.is_header_only == False
            )
            .order_by(Account.code.asc())
        )
        acc_res = await db.execute(acc_query)
        accounts = acc_res.scalars().all()

        # Query all posted lines up to as_of_date
        line_query = (
            select(
                JournalEntryLine.account_id,
                JournalEntryLine.debit,
                JournalEntryLine.credit
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.status == JournalStatus.POSTED.value,
                JournalEntry.entry_date <= as_of_date
            )
        )
        line_res = await db.execute(line_query)
        lines = line_res.all()

        # Aggregate by account
        acc_totals: Dict[str, Dict[str, Decimal]] = {
            acc.id: {"debit": Decimal("0.0"), "credit": Decimal("0.0")} for acc in accounts
        }

        for acc_id, debit, credit in lines:
            if acc_id in acc_totals:
                acc_totals[acc_id]["debit"] += debit
                acc_totals[acc_id]["credit"] += credit

        items = []
        total_debits = Decimal("0.0")
        total_credits = Decimal("0.0")

        for acc in accounts:
            deb = acc_totals[acc.id]["debit"]
            crd = acc_totals[acc.id]["credit"]

            # Compute net debit/credit side
            if acc.account_type in [AccountType.ASSET.value, AccountType.EXPENSE.value]:
                net = deb - crd
                deb_bal = net if net >= 0 else Decimal("0.0")
                crd_bal = -net if net < 0 else Decimal("0.0")
            else:
                net = crd - deb
                crd_bal = net if net >= 0 else Decimal("0.0")
                deb_bal = -net if net < 0 else Decimal("0.0")

            if deb_bal > 0 or crd_bal > 0:
                items.append(
                    TrialBalanceItem(
                        account_code=acc.code,
                        account_name=acc.name,
                        account_type=acc.account_type,
                        classification=acc.classification,
                        debit_balance=deb_bal,
                        credit_balance=crd_bal
                    )
                )
                total_debits += deb_bal
                total_credits += crd_bal

        is_balanced = abs(total_debits - total_credits) < Decimal("0.01")

        return TrialBalanceResponse(
            as_of_date=as_of_date,
            items=items,
            total_debits=total_debits,
            total_credits=total_credits,
            is_balanced=is_balanced
        )

    @classmethod
    async def generate_income_statement(
        cls,
        db: AsyncSession,
        tenant_id: str,
        start_date: date,
        end_date: date
    ) -> IncomeStatementResponse:
        """
        Generate Income Statement (Profit & Loss) for specified date range.
        """
        # Fetch revenue and expense accounts
        acc_query = (
            select(Account)
            .where(
                Account.tenant_id == tenant_id,
                Account.account_type.in_([AccountType.REVENUE.value, AccountType.EXPENSE.value]),
                Account.is_deleted == False
            )
        )
        acc_res = await db.execute(acc_query)
        accounts = {acc.id: acc for acc in acc_res.scalars().all()}

        # Fetch posted lines in date range
        line_query = (
            select(
                JournalEntryLine.account_id,
                JournalEntryLine.debit,
                JournalEntryLine.credit
            )
            .join(JournalEntry, JournalEntry.id == JournalEntryLine.journal_entry_id)
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.status == JournalStatus.POSTED.value,
                JournalEntry.entry_date >= start_date,
                JournalEntry.entry_date <= end_date
            )
        )
        line_res = await db.execute(line_query)
        lines = line_res.all()

        operating_revenue = Decimal("0.0")
        cogs = Decimal("0.0")
        opex = Decimal("0.0")
        other_income_exp = Decimal("0.0")
        tax_expense = Decimal("0.0")

        for acc_id, debit, credit in lines:
            acc = accounts.get(acc_id)
            if not acc:
                continue

            if acc.account_type == AccountType.REVENUE.value:
                net_rev = credit - debit
                if acc.classification == "OPERATING_REVENUE":
                    operating_revenue += net_rev
                else:
                    other_income_exp += net_rev
            elif acc.account_type == AccountType.EXPENSE.value:
                net_exp = debit - credit
                if acc.classification == "COST_OF_GOODS_SOLD":
                    cogs += net_exp
                elif acc.classification == "TAX_EXPENSE":
                    tax_expense += net_exp
                else:
                    opex += net_exp

        gross_profit = operating_revenue - cogs
        operating_income = gross_profit - opex
        net_income_before_tax = operating_income + other_income_exp
        net_profit = net_income_before_tax - tax_expense

        return IncomeStatementResponse(
            start_date=start_date,
            end_date=end_date,
            operating_revenue=operating_revenue,
            cost_of_goods_sold=cogs,
            gross_profit=gross_profit,
            operating_expenses=opex,
            operating_income=operating_income,
            other_income_expense=other_income_exp,
            net_income_before_tax=net_income_before_tax,
            tax_expense=tax_expense,
            net_profit=net_profit
        )

    @classmethod
    async def generate_balance_sheet(
        cls,
        db: AsyncSession,
        tenant_id: str,
        as_of_date: date
    ) -> BalanceSheetResponse:
        """
        Generate Balance Sheet showing Assets = Liabilities + Equity as of target date.
        """
        tb = await cls.generate_trial_balance(db, tenant_id, as_of_date)

        asset_items = []
        liability_items = []
        equity_items = []

        total_assets = Decimal("0.0")
        total_liabilities = Decimal("0.0")
        total_equity = Decimal("0.0")

        for item in tb.items:
            if item.account_type == AccountType.ASSET.value:
                bal = item.debit_balance - item.credit_balance
                asset_items.append({"code": item.account_code, "name": item.account_name, "amount": bal})
                total_assets += bal
            elif item.account_type == AccountType.LIABILITY.value:
                bal = item.credit_balance - item.debit_balance
                liability_items.append({"code": item.account_code, "name": item.account_name, "amount": bal})
                total_liabilities += bal
            elif item.account_type == AccountType.EQUITY.value:
                bal = item.credit_balance - item.debit_balance
                equity_items.append({"code": item.account_code, "name": item.account_name, "amount": bal})
                total_equity += bal

        # Calculate Year-to-Date retained earnings / profit to balance equity
        pnl = await cls.generate_income_statement(db, tenant_id, date(as_of_date.year, 1, 1), as_of_date)
        if pnl.net_profit != Decimal("0.0"):
            equity_items.append({"code": "YTD-PNL", "name": "Current Year Net Earnings", "amount": pnl.net_profit})
            total_equity += pnl.net_profit

        total_liab_equity = total_liabilities + total_equity
        is_balanced = abs(total_assets - total_liab_equity) < Decimal("0.01")

        return BalanceSheetResponse(
            as_of_date=as_of_date,
            assets=BalanceSheetSection(section_name="Assets", total_amount=total_assets, items=asset_items),
            liabilities=BalanceSheetSection(section_name="Liabilities", total_amount=total_liabilities, items=liability_items),
            equity=BalanceSheetSection(section_name="Equity", total_amount=total_equity, items=equity_items),
            total_assets=total_assets,
            total_liabilities_and_equity=total_liab_equity,
            is_balanced=is_balanced
        )
