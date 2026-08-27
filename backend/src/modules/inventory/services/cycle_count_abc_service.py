"""
NexERP ABC Inventory Classification & Perpetual Cycle Counting Engine.
Performs Pareto analysis (80/20 rule) based on annual inventory consumption value:
- Class A items (Top 80% value, ~10-20% items): Counted Monthly
- Class B items (Next 15% value, ~30% items): Counted Quarterly
- Class C items (Remaining 5% value, ~50% items): Counted Semi-Annually / Annually
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.inventory.models import Item, StockItemBalance


class ABCInventoryService:
    """
    Inventory Classification & Perpetual Cycle Counting Scheduling Service.
    """

    @classmethod
    def calculate_abc_classification(
        cls,
        inventory_items: List[Dict]
    ) -> List[Dict]:
        """
        Rank inventory items by annual dollar consumption value (Annual Volume x Unit Cost)
        and categorize into Class A, B, and C tiers.
        """
        if not inventory_items:
            return []

        # Calculate annual consumption value
        items_with_val = []
        for itm in inventory_items:
            qty = Decimal(str(itm.get("annual_consumption_qty", 100.0)))
            cost = Decimal(str(itm.get("unit_cost", 10.0)))
            val = qty * cost
            items_with_val.append({**itm, "_annual_value": val})

        # Sort descending by value
        items_with_val.sort(key=lambda x: x["_annual_value"], reverse=True)
        total_portfolio_value = sum(x["_annual_value"] for x in items_with_val)

        if total_portfolio_value == Decimal("0.0"):
            for x in items_with_val:
                x["abc_class"] = "C"
                x["count_frequency"] = "ANNUAL"
            return items_with_val

        running_cumulative_value = Decimal("0.0")
        classified = []

        for itm in items_with_val:
            running_cumulative_value += itm["_annual_value"]
            cum_pct = (running_cumulative_value / total_portfolio_value * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if cum_pct <= Decimal("80.0"):
                abc_class = "A"
                freq = "MONTHLY"
                count_cycles_per_year = 12
            elif cum_pct <= Decimal("95.0"):
                abc_class = "B"
                freq = "QUARTERLY"
                count_cycles_per_year = 4
            else:
                abc_class = "C"
                freq = "SEMI_ANNUALLY"
                count_cycles_per_year = 2

            classified.append({
                "item_id": itm.get("item_id"),
                "sku": itm.get("sku"),
                "name": itm.get("name"),
                "annual_consumption_value": float(itm["_annual_value"]),
                "cumulative_value_percent": float(cum_pct),
                "abc_class": abc_class,
                "recommended_count_frequency": freq,
                "count_cycles_per_year": count_cycles_per_year
            })

        return classified
