"""
NexERP Professional Services Automation (PSA) Resource Capacity & Billable Utilization Engine.
Tracks consultant billable target utilization percentages, bench capacity,
and revenue generation per full-time employee (FTE).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class ResourceManagementService:
    """
    PSA Resource Utilization and Bench Capacity Planning Service.
    """

    @classmethod
    def calculate_consultant_utilization(
        cls,
        total_available_hours: Decimal,
        billable_client_hours: Decimal,
        non_billable_pto_hours: Decimal = Decimal("0.0"),
        target_utilization_percent: Decimal = Decimal("75.0")
    ) -> Dict:
        """
        Compute standard PSA billable utilization rate (Billable Hours / Available Capacity Hours).
        """
        net_working_capacity = max(Decimal("1.0"), total_available_hours - non_billable_pto_hours)
        actual_utilization = ((billable_client_hours / net_working_capacity) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        variance_to_target = actual_utilization - target_utilization_percent

        return {
            "total_available_capacity_hours": float(total_available_hours),
            "billable_client_hours": float(billable_client_hours),
            "pto_holiday_hours": float(non_billable_pto_hours),
            "net_working_capacity_hours": float(net_working_capacity),
            "actual_utilization_percent": float(actual_utilization),
            "target_utilization_percent": float(target_utilization_percent),
            "utilization_variance_percent": float(variance_to_target),
            "utilization_rating": "EXCEEDS_TARGET" if variance_to_target >= Decimal("0.0") else "BELOW_TARGET"
        }
