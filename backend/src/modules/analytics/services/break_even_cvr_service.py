"""
NexERP Cost-Volume-Profit (CVP) & Break-Even Analysis Engine.
Calculates:
- Contribution Margin (CM) per unit & CM Ratio
- Break-Even Point in Units and in Currency Amount
- Margin of Safety (MOS) in Units, Currency, and Percentage
- Target Operating Income Sales Volume.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class BreakEvenAnalysisService:
    """
    Cost-Volume-Profit (CVP) and Break-Even Analysis Engine.
    """

    @classmethod
    def calculate_break_even_point(
        cls,
        selling_price_per_unit: Decimal,
        variable_cost_per_unit: Decimal,
        total_fixed_costs: Decimal,
        expected_unit_sales: Decimal,
        target_operating_income: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Compute CVP break-even thresholds and Margin of Safety.
        """
        unit_cm = selling_price_per_unit - variable_cost_per_unit
        if unit_cm <= Decimal("0.0"):
            raise ValueError("Selling price must exceed variable cost per unit (Contribution Margin must be positive).")

        cm_ratio = ((unit_cm / selling_price_per_unit) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Break-Even Units = Total Fixed Costs / Unit CM
        break_even_units = (total_fixed_costs / unit_cm).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        break_even_revenue = (break_even_units * selling_price_per_unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Target Income Units = (Fixed Costs + Target Income) / Unit CM
        target_units = ((total_fixed_costs + target_operating_income) / unit_cm).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        target_revenue = (target_units * selling_price_per_unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Margin of Safety (MOS)
        expected_revenue = expected_unit_sales * selling_price_per_unit
        mos_units = max(Decimal("0.0"), expected_unit_sales - break_even_units)
        mos_amount = max(Decimal("0.0"), expected_revenue - break_even_revenue)
        mos_percent = ((mos_amount / expected_revenue) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if expected_revenue > Decimal("0.0") else Decimal("0.0")

        # Operating Income at Expected Volume
        total_variable_costs = expected_unit_sales * variable_cost_per_unit
        total_contribution_margin = expected_unit_sales * unit_cm
        net_operating_income = total_contribution_margin - total_fixed_costs

        return {
            "selling_price_per_unit": float(selling_price_per_unit),
            "variable_cost_per_unit": float(variable_cost_per_unit),
            "unit_contribution_margin": float(unit_cm),
            "contribution_margin_ratio_percent": float(cm_ratio),
            "total_fixed_costs": float(total_fixed_costs),
            "break_even_point_units": float(break_even_units),
            "break_even_point_revenue": float(break_even_revenue),
            "target_operating_income_units": float(target_units),
            "target_operating_income_revenue": float(target_revenue),
            "expected_operating_income": float(net_operating_income),
            "margin_of_safety_units": float(mos_units),
            "margin_of_safety_revenue": float(mos_amount),
            "margin_of_safety_percent": float(mos_percent)
        }
