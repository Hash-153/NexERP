"""
Stochastic Safety Stock & Reorder Point Optimization Service.
Calculates dynamic safety buffers using standard normal distribution Z-scores and lead time variability.
"""
import math
from decimal import Decimal
from typing import Dict, Any

class StochasticSafetyStockService:
    # Service Level to Z-Score mapping
    SERVICE_LEVEL_Z_SCORES = {
        0.90: 1.28,
        0.95: 1.645,
        0.98: 2.05,
        0.99: 2.33,
        0.999: 3.09,
    }

    @classmethod
    def calculate_reorder_point(
        cls,
        daily_demand_mean: float,
        daily_demand_std_dev: float,
        lead_time_days_mean: float,
        lead_time_days_std_dev: float,
        target_service_level: float = 0.95
    ) -> Dict[str, Any]:
        z = cls.SERVICE_LEVEL_Z_SCORES.get(target_service_level, 1.645)

        # Average Demand during Lead Time (DDLT)
        avg_ddlt = daily_demand_mean * lead_time_days_mean

        # Combined Standard Deviation: sqrt(L * sigma_d^2 + d^2 * sigma_L^2)
        variance_demand_part = lead_time_days_mean * (daily_demand_std_dev ** 2)
        variance_lead_part = (daily_demand_mean ** 2) * (lead_time_days_std_dev ** 2)
        combined_std_dev = math.sqrt(variance_demand_part + variance_lead_part)

        # Safety Stock = Z * combined_std_dev
        safety_stock = z * combined_std_dev
        reorder_point = avg_ddlt + safety_stock

        return {
            "daily_demand_mean": daily_demand_mean,
            "lead_time_days_mean": lead_time_days_mean,
            "target_service_level_pct": target_service_level * 100,
            "z_score_multiplier": z,
            "average_lead_time_demand": round(avg_ddlt, 2),
            "calculated_safety_stock": round(safety_stock, 2),
            "optimized_reorder_point": round(reorder_point, 2),
            "buffer_days_equivalent": round(safety_stock / daily_demand_mean, 1) if daily_demand_mean > 0 else 0.0
        }
