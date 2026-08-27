"""
NexERP Advanced Pricing, Discount Matrices & Rebate Engine.
Evaluates multi-level price books, customer tier discounts, tiered volume breaks,
promotional discount coupons, and payment term cash discounts (e.g. 2/10 Net 30).
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class PricingEngineService:
    """
    Commercial Pricing & Quotation Matrix Engine.
    """

    @classmethod
    def calculate_effective_price(
        cls,
        base_list_price: Decimal,
        order_quantity: Decimal,
        customer_tier: str = "STANDARD",
        volume_breaks: Optional[List[Dict]] = None,
        promotional_discount_percent: Decimal = Decimal("0.0"),
        special_contract_price: Optional[Decimal] = None
    ) -> Dict:
        """
        Evaluate prioritized pricing hierarchy:
        1. Special Contract Override Price (if active)
        2. Volume Tier Break Discounts
        3. Customer Account Tier Discounts (VIP 10%, Wholesale 15%)
        4. Promotional Discounts
        """
        if special_contract_price is not None and special_contract_price > Decimal("0.0"):
            return {
                "pricing_rule_applied": "SPECIAL_CONTRACT_OVERRIDE",
                "base_list_price": float(base_list_price),
                "effective_unit_price": float(special_contract_price),
                "discount_percent": float(((base_list_price - special_contract_price) / base_list_price * Decimal("100.0")).quantize(Decimal("0.01"))) if base_list_price > Decimal("0.0") else 0.0,
                "total_order_amount": float((order_quantity * special_contract_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            }

        # Customer tier baseline discount
        tier_discounts = {
            "PLATINUM": Decimal("15.0"),
            "GOLD": Decimal("10.0"),
            "SILVER": Decimal("5.0"),
            "STANDARD": Decimal("0.0"),
        }
        tier_disc = tier_discounts.get(customer_tier.upper(), Decimal("0.0"))

        # Volume tier discount
        volume_disc = Decimal("0.0")
        if volume_breaks:
            # Sort volume breaks ascending by min_quantity
            sorted_breaks = sorted(volume_breaks, key=lambda x: Decimal(str(x.get("min_quantity", 0))))
            for b in sorted_breaks:
                min_q = Decimal(str(b.get("min_quantity", 0)))
                if order_quantity >= min_q:
                    volume_disc = max(volume_disc, Decimal(str(b.get("discount_percent", 0.0))))

        # Combine discounts (Best of tier vs volume + promotional)
        combined_discount = max(tier_disc, volume_disc) + promotional_discount_percent
        combined_discount = min(Decimal("50.0"), combined_discount)  # Cap max allowable discount at 50%

        discount_factor = (Decimal("100.0") - combined_discount) / Decimal("100.0")
        effective_price = (base_list_price * discount_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_amount = (order_quantity * effective_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "pricing_rule_applied": "TIER_AND_VOLUME_MATRIX",
            "base_list_price": float(base_list_price),
            "customer_tier": customer_tier,
            "tier_discount_percent": float(tier_disc),
            "volume_discount_percent": float(volume_disc),
            "promotional_discount_percent": float(promotional_discount_percent),
            "total_discount_percent": float(combined_discount),
            "effective_unit_price": float(effective_price),
            "total_order_amount": float(total_amount)
        }
