"""
NexERP Sales Incentive Compensation & Commission Engine.
Calculates sales representative commissions based on revenue targets, gross profit contribution margin,
and tiered quota accelerators (e.g. 100-120% quota = 1.5x accelerator, >120% = 2.0x).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class CommissionEngineService:
    """
    Sales Rep Incentive Compensation & Quota Acceleration Service.
    """

    @classmethod
    def calculate_rep_commission(
        cls,
        rep_id: str,
        rep_name: str,
        quota_target: Decimal,
        actual_revenue_achieved: Decimal,
        base_commission_rate_percent: Decimal = Decimal("5.0"),
        enable_accelerator: bool = True
    ) -> Dict:
        """
        Compute total commission payout for sales rep with tiered acceleration tiers.
        """
        if quota_target <= Decimal("0.0"):
            attainment_pct = Decimal("100.0")
        else:
            attainment_pct = ((actual_revenue_achieved / quota_target) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        base_commission = (actual_revenue_achieved * (base_commission_rate_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        accelerator_multiplier = Decimal("1.0")
        accelerator_bonus = Decimal("0.0")

        if enable_accelerator:
            if attainment_pct > Decimal("120.0"):
                # 2.0x multiplier on revenue above 120% of quota
                revenue_above_120 = actual_revenue_achieved - (quota_target * Decimal("1.20"))
                accelerator_bonus += (revenue_above_120 * (base_commission_rate_percent / Decimal("100.0")) * Decimal("1.0")).quantize(Decimal("0.01"))
                accelerator_multiplier = Decimal("2.0")
            elif attainment_pct > Decimal("100.0"):
                # 1.5x multiplier on revenue between 100% and 120%
                revenue_above_100 = actual_revenue_achieved - quota_target
                accelerator_bonus += (revenue_above_100 * (base_commission_rate_percent / Decimal("100.0")) * Decimal("0.5")).quantize(Decimal("0.01"))
                accelerator_multiplier = Decimal("1.5")

        total_payout = base_commission + accelerator_bonus

        return {
            "rep_id": rep_id,
            "rep_name": rep_name,
            "quota_target": float(quota_target),
            "actual_revenue": float(actual_revenue_achieved),
            "quota_attainment_percent": float(attainment_pct),
            "base_commission_rate_percent": float(base_commission_rate_percent),
            "base_commission_amount": float(base_commission),
            "accelerator_multiplier": float(accelerator_multiplier),
            "accelerator_bonus_amount": float(accelerator_bonus),
            "total_commission_payout": float(total_payout),
            "payout_status": "APPROVED_FOR_PAYROLL"
        }
