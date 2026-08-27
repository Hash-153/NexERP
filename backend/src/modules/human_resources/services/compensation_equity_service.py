"""
NexERP Compensation & Pay Equity Analytics Engine.
Calculates:
- Compa-Ratio = (Employee Actual Salary / Salary Grade Midpoint)
- Range Penetration = (Salary - Grade Min) / (Grade Max - Grade Min)
- Pay Equity Gaps across Gender / Demographics / Departments
- Merit Salary Increase Matrix based on Performance Rating and Compa-Ratio.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class CompensationAnalyticsService:
    """
    Compensation Band Grading and Pay Equity Analytics Service.
    """

    # Standard Merit Increase Matrix (Performance Rating x Compa-Ratio Quartile)
    # Returns recommended % salary increase
    MERIT_MATRIX = {
        ("EXCEEDS_EXPECTATIONS", "LOW_QUARTILE"): Decimal("7.0"),
        ("EXCEEDS_EXPECTATIONS", "MID_QUARTILE"): Decimal("5.5"),
        ("EXCEEDS_EXPECTATIONS", "HIGH_QUARTILE"): Decimal("4.0"),
        ("MEETS_EXPECTATIONS", "LOW_QUARTILE"): Decimal("4.5"),
        ("MEETS_EXPECTATIONS", "MID_QUARTILE"): Decimal("3.5"),
        ("MEETS_EXPECTATIONS", "HIGH_QUARTILE"): Decimal("2.5"),
        ("NEEDS_IMPROVEMENT", "LOW_QUARTILE"): Decimal("1.0"),
        ("NEETS_IMPROVEMENT", "MID_QUARTILE"): Decimal("0.0"),
        ("NEEDS_IMPROVEMENT", "HIGH_QUARTILE"): Decimal("0.0"),
    }

    @classmethod
    def calculate_employee_compa_ratio(
        cls,
        actual_salary: Decimal,
        grade_min: Decimal,
        grade_mid: Decimal,
        grade_max: Decimal
    ) -> Dict:
        """
        Compute Compa-Ratio, Range Penetration, and Quartile placement within salary band.
        """
        if grade_mid <= Decimal("0.0") or grade_max <= grade_min:
            raise ValueError("Grade midpoint and range span must be valid positive values.")

        compa_ratio = ((actual_salary / grade_mid) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        range_penetration = (((actual_salary - grade_min) / (grade_max - grade_min)) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if compa_ratio < Decimal("85.0"):
            quartile = "LOW_QUARTILE"
            band_position = "BELOW_BAND_ENTRY"
        elif compa_ratio <= Decimal("105.0"):
            quartile = "MID_QUARTILE"
            band_position = "MARKET_COMPETITIVE"
        else:
            quartile = "HIGH_QUARTILE"
            band_position = "TOP_OF_BAND"

        return {
            "actual_salary": float(actual_salary),
            "grade_min": float(grade_min),
            "grade_mid": float(grade_mid),
            "grade_max": float(grade_max),
            "compa_ratio_percent": float(compa_ratio),
            "range_penetration_percent": float(range_penetration),
            "quartile": quartile,
            "band_position": band_position
        }

    @classmethod
    def recommend_merit_increase(
        cls,
        current_salary: Decimal,
        performance_rating: str,
        grade_mid: Decimal
    ) -> Dict:
        """
        Evaluate merit increase based on market compa-ratio position and performance review.
        """
        compa = (current_salary / grade_mid) * Decimal("100.0") if grade_mid > Decimal("0.0") else Decimal("100.0")
        if compa < Decimal("90.0"):
            q = "LOW_QUARTILE"
        elif compa <= Decimal("110.0"):
            q = "MID_QUARTILE"
        else:
            q = "HIGH_QUARTILE"

        increase_pct = cls.MERIT_MATRIX.get((performance_rating.upper(), q), Decimal("3.0"))
        increase_amount = (current_salary * (increase_pct / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        new_salary = current_salary + increase_amount

        return {
            "current_salary": float(current_salary),
            "performance_rating": performance_rating.upper(),
            "compa_ratio_percent": float(compa.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "recommended_increase_percent": float(increase_pct),
            "annual_increase_amount": float(increase_amount),
            "new_base_salary": float(new_salary)
        }
