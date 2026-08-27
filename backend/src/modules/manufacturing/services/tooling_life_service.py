"""
NexERP Tooling, Die & Mold Life Cycle Management Engine.
Monitors:
- Tooling cumulative shot / hit / stroke count
- Expected tool life rating (e.g. 500,000 cycles for Carbide die)
- Maintenance sharpening / refurbishment triggers
- End-of-life amortization and tooling replacement alerts.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class ToolingLifeManagementService:
    """
    Stamping Die, Injection Mold & Tooling Life Tracking Service.
    """

    @classmethod
    def evaluate_tool_wear_status(
        cls,
        tool_id: str,
        tool_name: str,
        tool_type: str,
        total_lifetime_shots_rated: int,
        cumulative_shots_run: int,
        shots_since_last_sharpening: int,
        sharpening_interval_shots: int = 50000
    ) -> Dict:
        """
        Evaluate tool wear percentage, maintenance sharpening urgency, and remaining tool life.
        """
        remaining_lifetime_shots = max(0, total_lifetime_shots_rated - cumulative_shots_run)
        wear_percent = ((Decimal(str(cumulative_shots_run)) / Decimal(str(total_lifetime_shots_rated))) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        is_sharpening_due = shots_since_last_sharpening >= sharpening_interval_shots
        is_tool_end_of_life = cumulative_shots_run >= total_lifetime_shots_rated

        if is_tool_end_of_life:
            status = "EXPIRED_SCRAP_REQUIRED"
        elif is_sharpening_due:
            status = "SHARPENING_MAINTENANCE_DUE"
        elif wear_percent >= Decimal("85.0"):
            status = "APPROACHING_END_OF_LIFE"
        else:
            status = "OPERATIONAL_GOOD"

        return {
            "tool_id": tool_id,
            "tool_name": tool_name,
            "tool_type": tool_type,
            "total_lifetime_shots_rated": total_lifetime_shots_rated,
            "cumulative_shots_run": cumulative_shots_run,
            "shots_remaining": remaining_lifetime_shots,
            "tool_wear_percent": float(wear_percent),
            "shots_since_last_sharpening": shots_since_last_sharpening,
            "sharpening_interval_shots": sharpening_interval_shots,
            "is_sharpening_due": is_sharpening_due,
            "tool_status": status
        }
