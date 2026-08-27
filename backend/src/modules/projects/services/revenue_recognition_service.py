"""
NexERP Long-Term Project Revenue Recognition Engine (ASC 606 / IFRS 15).
Implements Over-Time / Percentage-of-Completion (PoC) revenue recognition using Cost-to-Cost method:
Recognized Revenue = Contract Value * (Cumulative Incurred Costs / Total Estimated Budget Costs).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class ProjectRevenueRecognitionService:
    """
    ASC 606 / IFRS 15 Project Revenue Recognition Engine.
    """

    @classmethod
    def calculate_poc_revenue_recognition(
        cls,
        total_contract_value: Decimal,
        total_estimated_budget_cost: Decimal,
        cumulative_incurred_cost: Decimal,
        previously_recognized_revenue: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Compute Cost-to-Cost Percentage of Completion (PoC) revenue earned in current accounting period.
        """
        if total_estimated_budget_cost <= Decimal("0.0"):
            poc_percent = Decimal("100.0")
        else:
            poc_percent = min(Decimal("100.0"), (cumulative_incurred_cost / total_estimated_budget_cost * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

        cumulative_earned_revenue = (total_contract_value * (poc_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        current_period_revenue_to_recognize = max(Decimal("0.0"), cumulative_earned_revenue - previously_recognized_revenue)

        return {
            "total_contract_value": float(total_contract_value),
            "total_estimated_budget_cost": float(total_estimated_budget_cost),
            "cumulative_incurred_cost": float(cumulative_incurred_cost),
            "percentage_of_completion_percent": float(poc_percent),
            "cumulative_earned_revenue": float(cumulative_earned_revenue),
            "previously_recognized_revenue": float(previously_recognized_revenue),
            "current_period_revenue_to_recognize": float(current_period_revenue_to_recognize),
            "unearned_contract_revenue_remaining": float(total_contract_value - cumulative_earned_revenue)
        }
