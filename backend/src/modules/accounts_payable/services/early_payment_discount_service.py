"""
NexERP AP Dynamic Early Payment Discount & Treasury Yield Optimization Engine.
Calculates terms like 2/10 Net 30, Annualized Percentage Rate (APR) yield on early settlement:
APR = [Discount % / (100% - Discount %)] * [365 / (Full Due Days - Discount Days)]
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class EarlyPaymentDiscountService:
    """
    Early Payment Settlement Discount & Working Capital Yield Engine.
    """

    @classmethod
    def calculate_early_payment_terms(
        cls,
        invoice_amount: Decimal,
        invoice_date: date,
        discount_percent: Decimal = Decimal("2.0"),
        discount_days: int = 10,
        net_due_days: int = 30
    ) -> Dict:
        """
        Compute early payment discount savings and annualized return (APR).
        """
        if net_due_days <= discount_days:
            raise ValueError("Net due days must be strictly greater than discount days.")

        discount_amount = (invoice_amount * (discount_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net_discounted_payment = invoice_amount - discount_amount

        discount_deadline = invoice_date + timedelta(days=discount_days)
        full_due_date = invoice_date + timedelta(days=net_due_days)

        days_saved = net_due_days - discount_days
        # APR Formula
        rate_factor = discount_percent / (Decimal("100.0") - discount_percent)
        time_factor = Decimal("365.0") / Decimal(str(days_saved))
        implied_apr = (rate_factor * time_factor * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "invoice_gross_amount": float(invoice_amount),
            "discount_percent": float(discount_percent),
            "discount_savings_amount": float(discount_amount),
            "net_discounted_payment_amount": float(net_discounted_payment),
            "discount_deadline_date": discount_deadline.isoformat(),
            "full_due_date": full_due_date.isoformat(),
            "days_accelerated": days_saved,
            "annualized_rate_of_return_apr_percent": float(implied_apr),
            "recommendation": "TAKE_DISCOUNT_HIGH_YIELD" if implied_apr >= Decimal("15.0") else "STANDARD_SETTLEMENT"
        }
