"""
Earned Value Management (EVM) Project Performance Analytics Engine.
Calculates Planned Value (PV), Earned Value (EV), Actual Cost (AC), SPI, CPI, and EAC.
"""
from decimal import Decimal
from typing import Dict, Any

class EarnedValueManagementService:
    @staticmethod
    def calculate_evm_metrics(
        budget_at_completion_bac: Decimal,
        planned_value_pv: Decimal,
        earned_value_ev: Decimal,
        actual_cost_ac: Decimal
    ) -> Dict[str, Any]:
        # Variances
        cost_variance_cv = earned_value_ev - actual_cost_ac
        schedule_variance_sv = earned_value_ev - planned_value_pv

        # Performance Indices
        cpi = (earned_value_ev / actual_cost_ac).quantize(Decimal("0.001")) if actual_cost_ac > 0 else Decimal("1.0")
        spi = (earned_value_ev / planned_value_pv).quantize(Decimal("0.001")) if planned_value_pv > 0 else Decimal("1.0")

        # Forecasts (Estimate at Completion EAC = BAC / CPI)
        eac = (budget_at_completion_bac / cpi).quantize(Decimal("0.01")) if cpi > 0 else budget_at_completion_bac
        variance_at_completion_vac = budget_at_completion_bac - eac

        return {
            "budget_at_completion_bac": float(budget_at_completion_bac),
            "planned_value_pv": float(planned_value_pv),
            "earned_value_ev": float(earned_value_ev),
            "actual_cost_ac": float(actual_cost_ac),
            "cost_variance_cv": float(cost_variance_cv),
            "schedule_variance_sv": float(schedule_variance_sv),
            "cost_performance_index_cpi": float(cpi),
            "schedule_performance_index_spi": float(spi),
            "estimate_at_completion_eac": float(eac),
            "variance_at_completion_vac": float(variance_at_completion_vac),
            "is_on_budget": bool(cpi >= Decimal("1.0")),
            "is_on_schedule": bool(spi >= Decimal("1.0")),
            "project_health": "EXCELLENT" if (cpi >= 1.0 and spi >= 1.0) else ("WARNING" if (cpi >= 0.9 or spi >= 0.9) else "CRITICAL_DISTRESS")
        }
