"""
NexERP Activity-Based Costing (ABC) Engine.
Allocates manufacturing and operational overhead to products via
cost driver rates rather than broad volume-based absorption:
- Identifies Activity Pools (Machine Setup, Quality Inspection, Logistics, Procurement)
- Calculates Cost Driver Rate = Pool Total Cost / Total Driver Volume
- Assigns ABC overhead per unit based on each product's driver consumption.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class ActivityBasedCostingService:
    """
    Activity-Based Costing (ABC) Overhead Absorption Engine.
    """

    @classmethod
    def calculate_abc_product_cost(
        cls,
        activity_pools: List[Dict],
        product_driver_matrix: Dict[str, Dict[str, Decimal]]
    ) -> Dict:
        """
        Compute per-unit ABC overhead for each product based on their driver consumption.

        activity_pools: list of {
            "activity_name": "Machine Setup",
            "total_pool_cost": Decimal("120000.0"),
            "driver_name": "setup_hours",
            "total_driver_volume": Decimal("600.0")
        }
        product_driver_matrix: {
            "PROD-A": {"setup_hours": Decimal("2.0"), "inspections": Decimal("1.0")},
            "PROD-B": {"setup_hours": Decimal("0.5"), "inspections": Decimal("3.0")}
        }
        """
        # Step 1: Compute cost driver rate per activity pool
        driver_rates: Dict[str, Decimal] = {}
        pool_summaries = []

        for pool in activity_pools:
            driver = pool["driver_name"]
            total_cost = Decimal(str(pool["total_pool_cost"]))
            total_vol = Decimal(str(pool["total_driver_volume"]))
            rate = (total_cost / total_vol).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if total_vol > Decimal("0.0") else Decimal("0.0")
            driver_rates[driver] = rate
            pool_summaries.append({
                "activity_name": pool["activity_name"],
                "driver_name": driver,
                "pool_cost": float(total_cost),
                "total_driver_volume": float(total_vol),
                "cost_driver_rate_per_unit": float(rate)
            })

        # Step 2: Assign overhead to each product
        product_abc_costs = {}
        for product_id, driver_consumption in product_driver_matrix.items():
            total_abc_overhead = Decimal("0.0")
            product_breakdown = []

            for driver, qty in driver_consumption.items():
                rate = driver_rates.get(driver, Decimal("0.0"))
                applied = (qty * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                total_abc_overhead += applied
                product_breakdown.append({
                    "driver": driver,
                    "consumption": float(qty),
                    "rate": float(rate),
                    "allocated_overhead": float(applied)
                })

            product_abc_costs[product_id] = {
                "total_abc_overhead_per_unit": float(total_abc_overhead),
                "driver_breakdown": product_breakdown
            }

        return {
            "activity_pools": pool_summaries,
            "product_abc_overhead": product_abc_costs
        }
