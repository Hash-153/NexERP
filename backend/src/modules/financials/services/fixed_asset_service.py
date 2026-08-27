"""
NexERP Fixed Asset Lifecycle and Depreciation Engine.
Supports Straight-Line (SLN), Double Declining Balance (DDB), Sum-of-the-Years'-Digits (SYD),
and MACRS tax depreciation schedules, asset impairment tests, and disposal gain/loss GL postings.
"""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.financials.models import FixedAsset, FiscalPeriod, Account
from backend.src.modules.financials.enums import DepreciationMethod
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate
from backend.src.modules.financials.services.general_ledger_service import GeneralLedgerService


class FixedAssetService:
    """
    Fixed Asset Management & Depreciation Engine.
    """

    @classmethod
    def calculate_depreciation_schedule(
        cls,
        acquisition_cost: Decimal,
        salvage_value: Decimal,
        useful_life_years: int,
        depreciation_method: str = "STRAIGHT_LINE",
        convention: str = "HALF_YEAR"
    ) -> List[Dict]:
        """
        Generate complete multi-year depreciation amortization schedule.
        """
        depreciable_base = acquisition_cost - salvage_value
        if depreciable_base <= Decimal("0.0") or useful_life_years <= 0:
            return []

        schedule = []
        accumulated_depreciation = Decimal("0.0")
        book_value = acquisition_cost

        if depreciation_method == DepreciationMethod.STRAIGHT_LINE.value:
            annual_rate = Decimal("1.0") / Decimal(str(useful_life_years))
            annual_depreciation = (depreciable_base * annual_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            for year_num in range(1, useful_life_years + 1):
                if year_num == useful_life_years:
                    expense = (depreciable_base - accumulated_depreciation).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                else:
                    expense = annual_depreciation

                accumulated_depreciation += expense
                book_value = acquisition_cost - accumulated_depreciation

                schedule.append({
                    "year": year_num,
                    "depreciation_expense": float(expense),
                    "monthly_expense": float((expense / Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    "accumulated_depreciation": float(accumulated_depreciation),
                    "ending_book_value": float(book_value)
                })

        elif depreciation_method == DepreciationMethod.DOUBLE_DECLINING_BALANCE.value:
            rate = (Decimal("2.0") / Decimal(str(useful_life_years)))

            for year_num in range(1, useful_life_years + 1):
                expense = (book_value * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if book_value - expense < salvage_value:
                    expense = max(Decimal("0.0"), book_value - salvage_value)

                accumulated_depreciation += expense
                book_value = acquisition_cost - accumulated_depreciation

                schedule.append({
                    "year": year_num,
                    "depreciation_expense": float(expense),
                    "monthly_expense": float((expense / Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    "accumulated_depreciation": float(accumulated_depreciation),
                    "ending_book_value": float(book_value)
                })

        elif depreciation_method == DepreciationMethod.SUM_OF_YEARS_DIGITS.value:
            sum_of_years = sum(range(1, useful_life_years + 1))
            for year_num in range(1, useful_life_years + 1):
                remaining_life = useful_life_years - year_num + 1
                factor = Decimal(str(remaining_life)) / Decimal(str(sum_of_years))
                expense = (depreciable_base * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

                accumulated_depreciation += expense
                book_value = acquisition_cost - accumulated_depreciation

                schedule.append({
                    "year": year_num,
                    "depreciation_expense": float(expense),
                    "monthly_expense": float((expense / Decimal("12.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                    "accumulated_depreciation": float(accumulated_depreciation),
                    "ending_book_value": float(book_value)
                })

        return schedule

    @classmethod
    async def post_monthly_depreciation_run(
        cls,
        db: AsyncSession,
        tenant_id: str,
        period_id: str,
        run_date: date,
        user_id: str = "system"
    ) -> List[Dict]:
        """
        Execute automated monthly depreciation posting for all active fixed assets.
        Generates and posts balancing debit (Depreciation Expense) and credit (Accumulated Depreciation).
        """
        period_res = await db.execute(
            select(FiscalPeriod).where(FiscalPeriod.id == period_id, FiscalPeriod.tenant_id == tenant_id)
        )
        period = period_res.scalar_one_or_none()
        if not period:
            raise EntityNotFoundError("Fiscal period not found.")

        # Query active assets
        assets_res = await db.execute(
            select(FixedAsset).where(
                FixedAsset.tenant_id == tenant_id,
                FixedAsset.is_depreciating == True,
                FixedAsset.is_deleted == False
            )
        )
        assets = list(assets_res.scalars().all())
        posted_records = []

        for asset in assets:
            if asset.current_book_value <= asset.salvage_value:
                continue

            monthly_deprec = (
                (asset.acquisition_cost - asset.salvage_value) /
                (Decimal(str(asset.useful_life_months)))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Cap at salvage value
            if asset.current_book_value - monthly_deprec < asset.salvage_value:
                monthly_deprec = max(Decimal("0.0"), asset.current_book_value - asset.salvage_value)

            if monthly_deprec <= Decimal("0.0"):
                continue

            # Create and post GL voucher
            gl_lines = [
                JournalEntryLineCreate(
                    account_id=asset.depreciation_expense_account_id,
                    debit=monthly_deprec,
                    credit=Decimal("0.0"),
                    description=f"Monthly Depreciation: {asset.asset_number} - {asset.name}"
                ),
                JournalEntryLineCreate(
                    account_id=asset.accumulated_depreciation_account_id,
                    debit=Decimal("0.0"),
                    credit=monthly_deprec,
                    description=f"Accumulated Depreciation: {asset.asset_number}"
                )
            ]

            jv_payload = JournalEntryCreate(
                entry_date=run_date,
                period_id=period.id,
                reference=f"DEPR-{asset.asset_number}-{run_date.strftime('%Y%m')}",
                narration=f"Fixed asset monthly amortization for {asset.name}",
                source_document_type="FixedAssetDepreciation",
                source_document_id=asset.id,
                lines=gl_lines
            )

            jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
            posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)

            # Update asset state
            asset.accumulated_depreciation = asset.accumulated_depreciation + monthly_deprec
            asset.current_book_value = asset.acquisition_cost - asset.accumulated_depreciation
            asset.last_depreciation_date = run_date

            posted_records.append({
                "asset_id": asset.id,
                "asset_number": asset.asset_number,
                "name": asset.name,
                "monthly_depreciation": float(monthly_deprec),
                "remaining_book_value": float(asset.current_book_value),
                "journal_id": posted_jv.id,
                "voucher_number": posted_jv.voucher_number
            })

        await db.commit()
        return posted_records
