"""
ASC 326 CECL (Current Expected Credit Losses) Allowance for Bad Debt Subsystem.
Estimates lifetime expected credit losses using historical default loss matrices and forward macroeconomic adjustments.
"""
from decimal import Decimal
from typing import Dict, Any, List

class CECLCreditLossAllowanceService:
    AGING_BUCKET_LOSS_RATES = {
        "CURRENT_0_30": Decimal("0.005"),    # 0.5% default probability
        "PAST_DUE_31_60": Decimal("0.025"),  # 2.5% default probability
        "PAST_DUE_61_90": Decimal("0.080"),  # 8.0% default probability
        "PAST_DUE_91_120": Decimal("0.250"), # 25.0% default probability
        "OVER_120_DAYS": Decimal("0.650"),   # 65.0% default probability
    }

    @classmethod
    def calculate_allowance_reserve(
        cls,
        ar_buckets: Dict[str, Decimal],
        macroeconomic_overlay_factor: Decimal = Decimal("1.15") # 15% recessionary adjustment
    ) -> Dict[str, Any]:
        total_gross_ar = Decimal("0.0")
        total_required_allowance = Decimal("0.0")
        bucket_details = []

        for bucket_key, rate in cls.AGING_BUCKET_LOSS_RATES.items():
            bucket_ar = ar_buckets.get(bucket_key, Decimal("0.0"))
            total_gross_ar += bucket_ar
            adjusted_rate = (rate * macroeconomic_overlay_factor).quantize(Decimal("0.0001"))
            allowance_amt = (bucket_ar * adjusted_rate).quantize(Decimal("0.01"))
            total_required_allowance += allowance_amt

            bucket_details.append({
                "bucket": bucket_key,
                "gross_ar": float(bucket_ar),
                "base_loss_rate": float(rate),
                "macro_adjusted_loss_rate": float(adjusted_rate),
                "expected_credit_loss": float(allowance_amt)
            })

        effective_coverage_pct = ((total_required_allowance / total_gross_ar) * Decimal("100.0")).quantize(Decimal("0.01")) if total_gross_ar > 0 else Decimal("0.0")

        return {
            "total_gross_ar": float(total_gross_ar),
            "total_cecl_allowance_reserve": float(total_required_allowance),
            "net_realizable_ar": float(total_gross_ar - total_required_allowance),
            "coverage_percentage": float(effective_coverage_pct),
            "macro_overlay_multiplier": float(macroeconomic_overlay_factor),
            "buckets": bucket_details
        }
