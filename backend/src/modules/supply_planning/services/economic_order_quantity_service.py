"""
Economic Order Quantity (EOQ) & Volume Discount Optimization Engine.
Minimizes total annual inventory holding costs and purchase order setup costs.
"""
import math
from decimal import Decimal
from typing import Dict, Any, List

class EconomicOrderQuantityService:
    @staticmethod
    def calculate_eoq(
        annual_demand_units: float,
        order_setup_cost: float,
        unit_cost: float,
        holding_cost_annual_rate: float = 0.20 # 20% annual holding rate
    ) -> Dict[str, Any]:
        annual_holding_per_unit = unit_cost * holding_cost_annual_rate
        if annual_holding_per_unit <= 0 or annual_demand_units <= 0:
            return {"optimal_order_quantity": 0, "annual_total_cost": 0.0}

        # Wilson EOQ Formula: sqrt((2 * D * S) / H)
        eoq = math.sqrt((2.0 * annual_demand_units * order_setup_cost) / annual_holding_per_unit)
        optimal_orders_per_year = annual_demand_units / eoq

        annual_order_cost = optimal_orders_per_year * order_setup_cost
        annual_holding_cost = (eoq / 2.0) * annual_holding_per_unit
        total_cost = (annual_demand_units * unit_cost) + annual_order_cost + annual_holding_cost

        return {
            "annual_demand_units": annual_demand_units,
            "unit_cost": unit_cost,
            "order_setup_cost": order_setup_cost,
            "annual_holding_rate_pct": holding_cost_annual_rate * 100,
            "optimal_order_quantity_eoq": round(eoq, 0),
            "orders_per_year": round(optimal_orders_per_year, 1),
            "cycle_stock_units": round(eoq / 2.0, 0),
            "annual_ordering_cost": round(annual_order_cost, 2),
            "annual_holding_cost": round(annual_holding_cost, 2),
            "total_annual_inventory_cost": round(total_cost, 2)
        }
