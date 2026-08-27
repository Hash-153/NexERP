"""
NexERP Stochastic Reorder Point (ROP) & Safety Stock Optimization Engine.
Calculates:
- Safety Stock: SS = Z * sqrt(Lead_Time * sigma_D^2 + Avg_Demand^2 * sigma_LT^2)
- Reorder Point (ROP) = (Average Daily Demand * Average Lead Time Days) + Safety Stock
- Economic Order Quantity (EOQ) = sqrt((2 * Annual_Demand * Order_Cost) / Holding_Cost_Per_Unit)
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional


class ReorderPointOptimizationService:
    """
    Inventory Safety Stock & Stochastic ROP Optimization Service.
    """

    # Service Level Z-Scores (Standard Normal Distribution)
    SERVICE_LEVEL_Z_FACTORS = {
        90.0: Decimal("1.282"),
        95.0: Decimal("1.645"),
        97.5: Decimal("1.960"),
        99.0: Decimal("2.326"),
        99.9: Decimal("3.090")
    }

    @classmethod
    def calculate_stochastic_rop(
        cls,
        avg_daily_demand: Decimal,
        daily_demand_std_dev: Decimal,
        avg_lead_time_days: Decimal,
        lead_time_std_dev_days: Decimal = Decimal("0.0"),
        target_service_level_percent: float = 95.0
    ) -> Dict:
        """
        Calculate statistical safety stock and dynamic reorder point threshold.
        """
        z_factor = cls.SERVICE_LEVEL_Z_FACTORS.get(target_service_level_percent, Decimal("1.645"))

        # Variance of demand during lead time: Var(DDLT) = (L * sigma_d^2) + (d^2 * sigma_L^2)
        term1 = float(avg_lead_time_days) * (float(daily_demand_std_dev) ** 2)
        term2 = (float(avg_daily_demand) ** 2) * (float(lead_time_std_dev_days) ** 2)
        sigma_ddlt = math.sqrt(term1 + term2)

        safety_stock = (z_factor * Decimal(str(sigma_ddlt))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        lead_time_demand = (avg_daily_demand * avg_lead_time_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        rop = lead_time_demand + safety_stock

        return {
            "avg_daily_demand": float(avg_daily_demand),
            "lead_time_days": float(avg_lead_time_days),
            "service_level_percent": target_service_level_percent,
            "z_factor": float(z_factor),
            "lead_time_demand": float(lead_time_demand),
            "safety_stock_units": float(safety_stock),
            "reorder_point_rop_units": float(rop)
        }

    @classmethod
    def calculate_economic_order_quantity(
        cls,
        annual_demand_units: Decimal,
        fixed_order_cost_usd: Decimal,
        annual_holding_cost_per_unit_usd: Decimal
    ) -> Dict:
        """
        Calculate Wilson EOQ and total inventory ordering/carrying costs.
        """
        if annual_holding_cost_per_unit_usd <= Decimal("0.0"):
            raise ValueError("Holding cost per unit must be positive.")

        eoq_raw = math.sqrt((2 * float(annual_demand_units) * float(fixed_order_cost_usd)) / float(annual_holding_cost_per_unit_usd))
        eoq_units = Decimal(str(eoq_raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        orders_per_year = (annual_demand_units / eoq_units).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        annual_ordering_cost = orders_per_year * fixed_order_cost_usd
        annual_holding_cost = (eoq_units / Decimal("2.0")) * annual_holding_cost_per_unit_usd
        total_cost = annual_ordering_cost + annual_holding_cost

        return {
            "economic_order_quantity_eoq": float(eoq_units),
            "orders_per_year": float(orders_per_year),
            "annual_ordering_cost": float(annual_ordering_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "annual_holding_cost": float(annual_holding_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            "total_annual_inventory_cost": float(total_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        }
