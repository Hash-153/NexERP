"""
ABC-XYZ Inventory Segmentation & Demand Volatility Matrix Service.
Segments items by annual dollar consumption (ABC) and coefficient of demand variation (XYZ).
"""
import math
from decimal import Decimal
from typing import Dict, Any, List

class ABCXYZInventorySegmentationService:
    @staticmethod
    def classify_sku(
        annual_spend: Decimal,
        monthly_demands: List[float],
        abc_spend_threshold_a: Decimal = Decimal("100000.00"),
        abc_spend_threshold_b: Decimal = Decimal("25000.00")
    ) -> Dict[str, Any]:
        # ABC Classification
        if annual_spend >= abc_spend_threshold_a:
            abc_class = "A"
        elif annual_spend >= abc_spend_threshold_b:
            abc_class = "B"
        else:
            abc_class = "C"

        # XYZ Classification (Coefficient of Variation: std_dev / mean)
        if len(monthly_demands) > 1:
            mean = sum(monthly_demands) / len(monthly_demands)
            variance = sum((x - mean) ** 2 for x in monthly_demands) / (len(monthly_demands) - 1)
            std_dev = math.sqrt(variance)
            cv = (std_dev / mean) if mean > 0 else 0.0
        else:
            cv = 0.0

        if cv < 0.25:
            xyz_class = "X" # Constant, predictable demand
        elif cv < 0.50:
            xyz_class = "Y" # Moderate fluctuation
        else:
            xyz_class = "Z" # Highly erratic demand

        segment = f"{abc_class}{xyz_class}"
        strategy_map = {
            "AX": "Automated JIT / VMI Kanban replenishment",
            "AY": "Safety stock buffered with weekly forecasts",
            "AZ": "Make-to-Order / Strict minimum order quantities",
            "BX": "Monthly periodic review reordering",
            "BY": "Safety stock reorder point with quarterly reviews",
            "BZ": "Demand-driven trigger only",
            "CX": "Bulk order discount stocking",
            "CY": "Standard reorder point buffer",
            "CZ": "Phase-out candidate / Made to order only",
        }

        return {
            "abc_class": abc_class,
            "xyz_class": xyz_class,
            "segment_code": segment,
            "annual_spend": float(annual_spend),
            "demand_coefficient_variation": round(cv, 4),
            "replenishment_strategy": strategy_map.get(segment, "Standard replenishment")
        }
