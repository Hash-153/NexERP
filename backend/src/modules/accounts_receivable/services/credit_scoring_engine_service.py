"""
NexERP Customer Credit Risk Scoring & Credit Limit Underwriting Engine.
Evaluates customer creditworthiness across 4 pillars:
1. Historical Payment Punctuality (Weighted on-time % over last 12 months)
2. Average Days Past Due (DPD)
3. Utilization of Existing Credit Line
4. Financial Solvency / Third-party Credit Score (e.g. Dun & Bradstreet / Paydex).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class CustomerCreditScoringService:
    """
    Customer Credit Underwriting and Credit Hold Management Service.
    """

    @classmethod
    def evaluate_customer_creditworthiness(
        cls,
        on_time_payment_rate_percent: Decimal,
        average_days_past_due: int,
        current_credit_limit: Decimal,
        current_outstanding_balance: Decimal,
        annual_sales_volume: Decimal,
        dnb_paydex_score: int = 80
    ) -> Dict:
        """
        Compute weighted composite credit score (0-100) and recommend credit limit actions.
        """
        # 1. Punctuality Score (Weight 35%)
        punctuality_score = on_time_payment_rate_percent * Decimal("0.35")

        # 2. Days Past Due Score (Weight 25%)
        if average_days_past_due <= 0:
            dpd_points = Decimal("100.0")
        elif average_days_past_due <= 15:
            dpd_points = Decimal("80.0")
        elif average_days_past_due <= 30:
            dpd_points = Decimal("50.0")
        elif average_days_past_due <= 60:
            dpd_points = Decimal("20.0")
        else:
            dpd_points = Decimal("0.0")
        dpd_score = dpd_points * Decimal("0.25")

        # 3. Credit Utilization Score (Weight 20%)
        utilization_pct = ((current_outstanding_balance / current_credit_limit) * Decimal("100.0")) if current_credit_limit > Decimal("0.0") else Decimal("100.0")
        if utilization_pct <= Decimal("50.0"):
            util_points = Decimal("100.0")
        elif utilization_pct <= Decimal("80.0"):
            util_points = Decimal("75.0")
        elif utilization_pct <= Decimal("100.0"):
            util_points = Decimal("40.0")
        else:
            util_points = Decimal("0.0")
        util_score = util_points * Decimal("0.20")

        # 4. Third-Party Score (Weight 20%)
        dnb_points = Decimal(str(min(100, max(0, dnb_paydex_score))))
        dnb_score = dnb_points * Decimal("0.20")

        composite_credit_score = (punctuality_score + dpd_score + util_score + dnb_score).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Recommendation and Credit Limit Adjustment
        if composite_credit_score >= Decimal("85.0"):
            risk_tier = "PRIME_LOW_RISK"
            credit_hold = False
            recommended_max_limit = (annual_sales_volume * Decimal("0.15")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif composite_credit_score >= Decimal("70.0"):
            risk_tier = "STANDARD_MODERATE_RISK"
            credit_hold = False
            recommended_max_limit = (annual_sales_volume * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        elif composite_credit_score >= Decimal("50.0"):
            risk_tier = "WATCHLIST_ELEVATED_RISK"
            credit_hold = current_outstanding_balance >= current_credit_limit
            recommended_max_limit = current_credit_limit
        else:
            risk_tier = "HIGH_DEFAULT_RISK"
            credit_hold = True
            recommended_max_limit = Decimal("0.0")  # Cash in Advance / COD required

        return {
            "composite_credit_score": float(composite_credit_score),
            "risk_tier": risk_tier,
            "credit_hold_triggered": credit_hold,
            "current_credit_limit": float(current_credit_limit),
            "current_outstanding_balance": float(current_outstanding_balance),
            "credit_utilization_percent": float(utilization_pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "recommended_credit_limit": float(recommended_max_limit),
            "score_breakdown": {
                "punctuality_points": float(punctuality_score),
                "days_past_due_points": float(dpd_score),
                "credit_utilization_points": float(util_score),
                "external_rating_points": float(dnb_score)
            }
        }
