"""
NexERP Configure, Price, Quote (CPQ) Rules & Validation Engine.
Validates:
- Option Compatibility (e.g. 500kW Motor requires Heavy-Duty Inverter)
- Mutually Exclusive Features (e.g. Cannot select both Pneumatic and Hydraulic Actuator)
- Mandatory Co-requisites (e.g. Hazardous Area Certification requires ATEX Enclosure)
- Parametric Option Pricing Add-ons.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class CPQRulesEngineService:
    """
    Parametric CPQ Product Configuration & Compatibility Engine.
    """

    # Standard Engineering Compatibility Rules Matrix
    COMPATIBILITY_RULES = [
        {
            "rule_id": "RULE-MOTOR-PWR",
            "condition_feature": "MOTOR_500KW",
            "required_co_requisites": ["INVERTER_HD_HEAVY_DUTY"],
            "mutually_exclusive_with": ["POWER_SUPPLY_STANDARD_100A"],
            "description": "500kW Motor requires Heavy-Duty Inverter and is incompatible with Standard 100A supply."
        },
        {
            "rule_id": "RULE-ATEX-HAZ",
            "condition_feature": "ZONE_1_EXPLOSION_PROOF",
            "required_co_requisites": ["ENCLOSURE_STAINLESS_IP68", "FLAMEPROOF_GLAND_SET"],
            "mutually_exclusive_with": ["ENCLOSURE_STANDARD_PLASTIC"],
            "description": "Explosion-proof certification requires IP68 stainless enclosure and flameproof glands."
        }
    ]

    @classmethod
    def validate_configuration(
        cls,
        base_product_sku: str,
        base_price: Decimal,
        selected_features: List[str],
        feature_price_table: Dict[str, Decimal]
    ) -> Dict:
        """
        Validate feature combination against CPQ constraints and compute configured total quote price.
        """
        violations = []
        selected_set = set(selected_features)

        # Check compatibility rules
        for rule in cls.COMPATIBILITY_RULES:
            if rule["condition_feature"] in selected_set:
                # Check co-requisites
                for req in rule["required_co_requisites"]:
                    if req not in selected_set:
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "violation_type": "MISSING_CO_REQUISITE",
                            "message": f"Selecting '{rule['condition_feature']}' requires mandatory option '{req}'."
                        })

                # Check mutual exclusions
                for exc in rule["mutually_exclusive_with"]:
                    if exc in selected_set:
                        violations.append({
                            "rule_id": rule["rule_id"],
                            "violation_type": "MUTUALLY_EXCLUSIVE_CONFLICT",
                            "message": f"'{rule['condition_feature']}' cannot be selected together with '{exc}'."
                        })

        # Calculate Price Breakdown
        options_total = Decimal("0.0")
        price_breakdown = []
        for feat in selected_features:
            p = feature_price_table.get(feat, Decimal("0.0"))
            options_total += p
            price_breakdown.append({"feature_code": feat, "unit_price": float(p)})

        total_configured_price = base_price + options_total

        return {
            "base_product_sku": base_product_sku,
            "base_price": float(base_price),
            "selected_options_count": len(selected_features),
            "options_total_price": float(options_total),
            "total_configured_quote_price": float(total_configured_price),
            "is_configuration_valid": len(violations) == 0,
            "configuration_violations": violations,
            "pricing_breakdown": price_breakdown
        }
