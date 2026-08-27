"""
NexERP Project Earned Value Management (EVM) & Cost Engineering Engine.
Calculates ANSI/EIA-748 standard project performance metrics:
- Planned Value (PV / BCWS)
- Earned Value (EV / BCWP)
- Actual Cost (AC / ACWP)
- Cost Variance (CV) & Schedule Variance (SV)
- Cost Performance Index (CPI) & Schedule Performance Index (SPI)
- Estimate At Completion (EAC) & To-Complete Performance Index (TCPI).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class EarnedValueService:
    """
    Project Earned Value Analysis & Cost Engineering Service.
    """

    @classmethod
    def calculate_project_evm_metrics(
        cls,
        budget_at_completion: Decimal,
        percent_work_completed: Decimal,
        planned_percent_at_date: Decimal,
        actual_cost_incurred: Decimal
    ) -> Dict:
        """
        Compute standard ANSI-748 Earned Value metrics.
        """
        # Planned Value (PV) = BAC * Planned %
        pv = (budget_at_completion * (planned_percent_at_date / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Earned Value (EV) = BAC * Actual %
        ev = (budget_at_completion * (percent_work_completed / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Actual Cost (AC)
        ac = actual_cost_incurred

        # Variances
        cost_variance = (ev - ac).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        schedule_variance = (ev - pv).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Indices
        cpi = (ev / ac).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if ac > Decimal("0.0") else Decimal("1.0")
        spi = (ev / pv).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if pv > Decimal("0.0") else Decimal("1.0")

        # Estimate at Completion (EAC) = BAC / CPI
        if cpi > Decimal("0.0"):
            eac = (budget_at_completion / cpi).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            eac = budget_at_completion

        variance_at_completion = budget_at_completion - eac

        return {
            "budget_at_completion": float(budget_at_completion),
            "planned_value_pv": float(pv),
            "earned_value_ev": float(ev),
            "actual_cost_ac": float(ac),
            "cost_variance_cv": float(cost_variance),
            "schedule_variance_sv": float(schedule_variance),
            "cost_performance_index_cpi": float(cpi),
            "schedule_performance_index_spi": float(spi),
            "estimate_at_completion_eac": float(eac),
            "variance_at_completion_vac": float(variance_at_completion),
            "cost_status": "UNDER_BUDGET" if cost_variance >= Decimal("0.0") else "OVER_BUDGET",
            "schedule_status": "AHEAD_OF_SCHEDULE" if schedule_variance >= Decimal("0.0") else "BEHIND_SCHEDULE"
        }
