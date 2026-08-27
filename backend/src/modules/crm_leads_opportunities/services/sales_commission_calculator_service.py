"""
Sales Commission & Tiered Quota Accelerator Calculation Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List

class SalesCommissionCalculatorService:
    @staticmethod
    def calculate_rep_payout(
        quota_target: Decimal,
        actual_closed_revenue: Decimal,
        base_commission_rate_pct: Decimal = Decimal("10.0"),
        tier_1_accelerator_pct: Decimal = Decimal("15.0"), # 100% - 120% of quota
        tier_2_accelerator_pct: Decimal = Decimal("20.0")  # >120% of quota
    ) -> Dict[str, Any]:
        quota_attainment_pct = ((actual_closed_revenue / quota_target) * Decimal("100.0")).quantize(Decimal("0.01")) if quota_target > 0 else Decimal("0.0")
        
        base_rate = base_commission_rate_pct / Decimal("100.0")
        t1_rate = tier_1_accelerator_pct / Decimal("100.0")
        t2_rate = tier_2_accelerator_pct / Decimal("100.0")

        payout = Decimal("0.0")
        tier_breakdown = []

        if actual_closed_revenue <= quota_target:
            # Below or at quota
            payout = actual_closed_revenue * base_rate
            tier_breakdown.append({"tier": "Base (<100%)", "revenue": float(actual_closed_revenue), "rate": float(base_rate), "commission": float(payout)})
        else:
            # 1. Base tier to 100%
            base_comm = quota_target * base_rate
            payout += base_comm
            tier_breakdown.append({"tier": "Base (100% Quota)", "revenue": float(quota_target), "rate": float(base_rate), "commission": float(base_comm)})
            
            excess_rev = actual_closed_revenue - quota_target
            t1_cap = quota_target * Decimal("0.20")  # Next 20%
            
            if excess_rev <= t1_cap:
                t1_comm = excess_rev * t1_rate
                payout += t1_comm
                tier_breakdown.append({"tier": "Tier 1 Accelerator (100-120%)", "revenue": float(excess_rev), "rate": float(t1_rate), "commission": float(t1_comm)})
            else:
                t1_comm = t1_cap * t1_rate
                payout += t1_comm
                tier_breakdown.append({"tier": "Tier 1 Accelerator (100-120%)", "revenue": float(t1_cap), "rate": float(t1_rate), "commission": float(t1_comm)})
                
                t2_rev = excess_rev - t1_cap
                t2_comm = t2_rev * t2_rate
                payout += t2_comm
                tier_breakdown.append({"tier": "Tier 2 Super Accelerator (>120%)", "revenue": float(t2_rev), "rate": float(t2_rate), "commission": float(t2_comm)})

        return {
            "quota_target": float(quota_target),
            "actual_closed_revenue": float(actual_closed_revenue),
            "attainment_percentage": float(quota_attainment_pct),
            "total_commission_payout": float(payout.quantize(Decimal("0.01"))),
            "effective_commission_rate": float(((payout / actual_closed_revenue) * Decimal("100.0")).quantize(Decimal("0.01"))) if actual_closed_revenue > 0 else 0.0,
            "tiers": tier_breakdown
        }
