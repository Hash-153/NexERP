"""
Multi-Currency FX Triangulation & Cross-Rate Engine.
Performs currency conversions through base bridge currencies (USD/EUR) with bid-ask spread handling.
"""
from decimal import Decimal
from typing import Dict, Any, List

class FXCrossCurrencyTriangulationService:
    # Direct spot rates against USD (Base = USD)
    USD_SPOT_RATES = {
        "EUR": Decimal("1.0850"),
        "GBP": Decimal("1.2650"),
        "JPY": Decimal("0.00665"),
        "CAD": Decimal("0.7350"),
        "AUD": Decimal("0.6550"),
        "CHF": Decimal("1.1250"),
        "SGD": Decimal("0.7450"),
        "INR": Decimal("0.01205"),
        "USD": Decimal("1.0000"),
    }

    @classmethod
    def convert_amount(
        cls,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        bid_ask_spread_bps: int = 15  # 15 basis points spread
    ) -> Dict[str, Any]:
        from_curr = from_currency.upper()
        to_curr = to_currency.upper()

        if from_curr == to_curr:
            return {
                "original_amount": float(amount),
                "converted_amount": float(amount),
                "from_currency": from_curr,
                "to_currency": to_curr,
                "cross_rate": 1.0,
                "fee_spread": 0.0
            }

        rate_from_usd = cls.USD_SPOT_RATES.get(from_curr, Decimal("1.0"))
        rate_to_usd = cls.USD_SPOT_RATES.get(to_curr, Decimal("1.0"))

        # Amount in USD = Amount * (Rate From USD)
        usd_value = amount * rate_from_usd
        # Amount in To Currency = USD Value / (Rate To USD)
        raw_converted = usd_value / rate_to_usd
        cross_rate = rate_from_usd / rate_to_usd

        # Apply spread
        spread_fraction = Decimal(str(bid_ask_spread_bps)) / Decimal("10000.0")
        spread_cost = raw_converted * spread_fraction
        final_amount = (raw_converted - spread_cost).quantize(Decimal("0.01"))

        return {
            "original_amount": float(amount),
            "converted_amount": float(final_amount),
            "from_currency": from_curr,
            "to_currency": to_curr,
            "cross_rate": float(cross_rate.quantize(Decimal("0.000001"))),
            "bid_ask_spread_cost": float(spread_cost.quantize(Decimal("0.01"))),
            "triangulation_bridge": "USD"
        }
