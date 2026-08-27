"""
NexERP FMLA (Family and Medical Leave Act) & PTO Accrual Policy Engine.
Tracks:
- Rolling 12-month FMLA 12-week (480 hours) job-protected entitlement
- Bi-weekly and monthly Paid Time Off (PTO) accruals based on tenure seniority
- Maximum PTO carryover caps and forfeiture balances at year-end.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class FMLALeaveAccrualService:
    """
    FMLA Tracking & PTO Seniority Tier Accrual Service.
    """

    # Tenure Seniority PTO Accrual Tiers: (Years of Service, Annual PTO Hours, Max Carryover Hours)
    PTO_TENURE_TIERS = [
        (0, Decimal("120.0"), Decimal("40.0")),  # 0-2 yrs: 15 days/yr
        (3, Decimal("160.0"), Decimal("80.0")),  # 3-5 yrs: 20 days/yr
        (6, Decimal("200.0"), Decimal("120.0")), # 6+ yrs: 25 days/yr
    ]

    @classmethod
    def calculate_fmla_rolling_entitlement(
        cls,
        as_of_date: date,
        past_12_month_fmla_leaves: List[Dict],
        total_statutory_fmla_hours: Decimal = Decimal("480.0")
    ) -> Dict:
        """
        Compute available FMLA hours using the Department of Labor rolling 12-month lookback method.
        """
        one_year_prior = as_of_date - timedelta(days=365)
        hours_used_in_lookback = Decimal("0.0")

        for leave in past_12_month_fmla_leaves:
            l_date = leave["start_date"]
            if l_date >= one_year_prior and l_date <= as_of_date:
                hours_used_in_lookback += Decimal(str(leave["hours_taken"]))

        hours_remaining = max(Decimal("0.0"), total_statutory_fmla_hours - hours_used_in_lookback)

        return {
            "as_of_date": as_of_date.isoformat(),
            "lookback_start_date": one_year_prior.isoformat(),
            "statutory_total_fmla_hours": float(total_statutory_fmla_hours),
            "hours_used_in_12mo_window": float(hours_used_in_lookback),
            "hours_remaining_available": float(hours_remaining),
            "weeks_remaining": float((hours_remaining / Decimal("40.0")).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
            "entitlement_exhausted": hours_remaining <= Decimal("0.0")
        }

    @classmethod
    def calculate_periodic_pto_accrual(
        cls,
        years_of_service: int,
        current_accrued_balance: Decimal,
        pay_periods_per_year: int = 24  # Semi-monthly
    ) -> Dict:
        """
        Calculate employee's earned PTO credit per pay cycle and check against accrual caps.
        """
        # Determine applicable tier
        annual_hours = Decimal("120.0")
        max_carryover = Decimal("40.0")
        for min_years, ann_hrs, carry in cls.PTO_TENURE_TIERS:
            if years_of_service >= min_years:
                annual_hours = ann_hrs
                max_carryover = carry

        accrual_per_period = (annual_hours / Decimal(str(pay_periods_per_year))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        max_cap = annual_hours * Decimal("1.5")  # Max accrual ceiling is 1.5x annual allotment

        projected_balance = current_accrued_balance + accrual_per_period
        is_capped = projected_balance > max_cap
        actual_accrued = max(Decimal("0.0"), max_cap - current_accrued_balance) if is_capped else accrual_per_period
        new_balance = current_accrued_balance + actual_accrued

        return {
            "years_of_service": years_of_service,
            "annual_pto_allotment_hours": float(annual_hours),
            "accrual_per_pay_period": float(accrual_per_period),
            "current_balance": float(current_accrued_balance),
            "earned_this_period": float(actual_accrued),
            "new_pto_balance": float(new_balance),
            "max_accrual_cap": float(max_cap),
            "is_accrual_capped": is_capped,
            "max_year_end_carryover_hours": float(max_carryover)
        }
