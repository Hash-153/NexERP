"""
NexERP Manufacturing Scrap & Material Yield Variance Accounting Engine.
Calculates:
- Standard Expected Scrap (from BOM scrap % factors)
- Actual Incurred Scrap during Job Execution
- Material Yield Variance = (Actual Units Produced - Standard Expected Units) * Standard Unit Cost
- Material Scrap Variance = (Actual Scrap Units - Standard Scrap Allowance) * Standard Unit Cost.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class ScrapVarianceService:
    """
    Manufacturing Yield and Scrap Variance Analysis Service.
    """

    @classmethod
    def calculate_job_scrap_variance(
        cls,
        production_order_number: str,
        item_sku: str,
        total_input_units: Decimal,
        standard_scrap_percent: Decimal,
        actual_scrap_units: Decimal,
        standard_unit_cost: Decimal
    ) -> Dict:
        """
        Compute standard scrap allowance vs actual scrap defectives and financial variance.
        """
        standard_scrap_allowed = (total_input_units * (standard_scrap_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        expected_good_output = total_input_units - standard_scrap_allowed
        actual_good_output = total_input_units - actual_scrap_units

        # Scrap Variance (in units and dollars)
        scrap_variance_units = actual_scrap_units - standard_scrap_allowed
        scrap_variance_cost = (scrap_variance_units * standard_unit_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        actual_scrap_percent = ((actual_scrap_units / total_input_units) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_input_units > Decimal("0.0") else Decimal("0.0")
        actual_yield_percent = Decimal("100.0") - actual_scrap_percent

        return {
            "production_order_number": production_order_number,
            "item_sku": item_sku,
            "total_input_units": float(total_input_units),
            "standard_scrap_percent": float(standard_scrap_percent),
            "standard_scrap_allowed_units": float(standard_scrap_allowed),
            "actual_scrap_units": float(actual_scrap_units),
            "actual_scrap_percent": float(actual_scrap_percent),
            "actual_yield_percent": float(actual_yield_percent),
            "actual_good_units_produced": float(actual_good_output),
            "scrap_variance_units": float(scrap_variance_units),
            "scrap_variance_cost_usd": float(scrap_variance_cost),
            "variance_type": "UNFAVORABLE" if scrap_variance_cost > Decimal("0.0") else "FAVORABLE",
            "gl_variance_entry": {
                "debit_account": "Manufacturing Scrap Variance (P&L)",
                "credit_account": "Work in Process (WIP) Inventory",
                "amount": float(scrap_variance_cost)
            } if scrap_variance_cost > Decimal("0.0") else None
        }
