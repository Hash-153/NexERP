"""
Supplier Early Payment Dynamic Discounting & Sliding APR Yield Engine.
Calculates annualized internal rate of return (APR) on early vendor bill settlements (e.g. 2/10 Net 30).
"""
from decimal import Decimal
from typing import Dict, Any

class SupplierEarlyPayDynamicDiscountEngine:
    @staticmethod
    def calculate_sliding_discount(
        bill_amount: Decimal,
        standard_terms_days: int = 30,
        early_pay_day: int = 10,
        offered_discount_pct: Decimal = Decimal("2.0")  # 2% standard
    ) -> Dict[str, Any]:
        days_accelerated = standard_terms_days - early_pay_day
        if days_accelerated <= 0:
            return {
                "bill_amount": float(bill_amount),
                "discount_amount": 0.0,
                "net_payable": float(bill_amount),
                "annualized_apr_return": 0.0
            }

        discount_amount = (bill_amount * (offered_discount_pct / Decimal("100.0"))).quantize(Decimal("0.01"))
        net_payable = bill_amount - discount_amount

        # Annualized APR Formula: (Discount% / (100% - Discount%)) * (365 / Days Accelerated)
        discount_fraction = offered_discount_pct / (Decimal("100.0") - offered_discount_pct)
        time_multiplier = Decimal("365.0") / Decimal(str(days_accelerated))
        annualized_apr = (discount_fraction * time_multiplier * Decimal("100.0")).quantize(Decimal("0.01"))

        return {
            "original_bill_amount": float(bill_amount),
            "days_accelerated": days_accelerated,
            "discount_percentage": float(offered_discount_pct),
            "discount_cash_saved": float(discount_amount),
            "net_payment_amount": float(net_payable),
            "annualized_apr_return": float(annualized_apr),
            "recommendation": "EXECUTE_EARLY_PAYMENT" if annualized_apr >= Decimal("12.0") else "PAY_ON_DUE_DATE"
        }
