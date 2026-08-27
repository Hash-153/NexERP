"""
NexERP Accounts Receivable ASC 326 CECL (Current Expected Credit Losses) & Aging Engine.
Classifies outstanding customer invoices into standardized aging buckets:
- Current (0-30 days)
- 31-60 days
- 61-90 days
- 91-120 days
- 120+ days
and computes historical loss-rate provisions for doubtful accounts.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class ARAgingAnalysisService:
    """
    AR Aging and ASC 326 CECL Allowance for Doubtful Accounts Service.
    """

    # Default CECL Historical Loss Rate Reserves by Aging Bracket
    DEFAULT_LOSS_RATES = {
        "CURRENT_0_30": Decimal("0.005"),     # 0.5%
        "PAST_DUE_31_60": Decimal("0.020"),   # 2.0%
        "PAST_DUE_61_90": Decimal("0.080"),   # 8.0%
        "PAST_DUE_91_120": Decimal("0.250"),  # 25.0%
        "PAST_DUE_120_PLUS": Decimal("0.600") # 60.0%
    }

    @classmethod
    def calculate_ar_aging_and_provisions(
        cls,
        invoices: List[Dict],
        as_of_date: date,
        custom_loss_rates: Dict[str, Decimal] = None
    ) -> Dict:
        """
        Group invoices into aging buckets and compute CECL bad debt allowance.
        """
        loss_rates = custom_loss_rates or cls.DEFAULT_LOSS_RATES

        buckets = {
            "CURRENT_0_30": {"invoices": [], "total_amount": Decimal("0.0")},
            "PAST_DUE_31_60": {"invoices": [], "total_amount": Decimal("0.0")},
            "PAST_DUE_61_90": {"invoices": [], "total_amount": Decimal("0.0")},
            "PAST_DUE_91_120": {"invoices": [], "total_amount": Decimal("0.0")},
            "PAST_DUE_120_PLUS": {"invoices": [], "total_amount": Decimal("0.0")},
        }

        total_outstanding = Decimal("0.0")

        for inv in invoices:
            due_date = inv["due_date"]
            balance = Decimal(str(inv["open_balance"]))
            if balance <= Decimal("0.0"):
                continue

            total_outstanding += balance
            days_overdue = (as_of_date - due_date).days

            if days_overdue <= 30:
                bucket_key = "CURRENT_0_30"
            elif days_overdue <= 60:
                bucket_key = "PAST_DUE_31_60"
            elif days_overdue <= 90:
                bucket_key = "PAST_DUE_61_90"
            elif days_overdue <= 120:
                bucket_key = "PAST_DUE_91_120"
            else:
                bucket_key = "PAST_DUE_120_PLUS"

            buckets[bucket_key]["invoices"].append({
                "invoice_number": inv.get("invoice_number"),
                "customer_name": inv.get("customer_name"),
                "due_date": due_date.isoformat(),
                "days_overdue": days_overdue,
                "amount": float(balance)
            })
            buckets[bucket_key]["total_amount"] += balance

        # Calculate CECL Reserves
        total_cecl_reserve = Decimal("0.0")
        bucket_summaries = {}

        for b_name, b_data in buckets.items():
            b_amt = b_data["total_amount"]
            loss_rate = loss_rates.get(b_name, Decimal("0.0"))
            reserve = (b_amt * loss_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total_cecl_reserve += reserve

            bucket_summaries[b_name] = {
                "total_amount": float(b_amt),
                "count": len(b_data["invoices"]),
                "loss_rate_percent": float(loss_rate * Decimal("100.0")),
                "required_cecl_reserve": float(reserve)
            }

        effective_reserve_rate = ((total_cecl_reserve / total_outstanding) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_outstanding > Decimal("0.0") else Decimal("0.0")

        return {
            "as_of_date": as_of_date.isoformat(),
            "total_ar_outstanding": float(total_outstanding),
            "total_cecl_bad_debt_reserve": float(total_cecl_reserve),
            "effective_reserve_rate_percent": float(effective_reserve_rate),
            "aging_buckets": bucket_summaries
        }
