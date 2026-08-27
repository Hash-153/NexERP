"""
Cost Center Step-Down & Reciprocal Overhead Allocation Engine.
Allocates service department costs (IT, HR, Facilities) down to revenue-producing business units.
"""
from decimal import Decimal
from typing import Dict, Any, List

class CostCenterStepDownAllocationService:
    @staticmethod
    def step_down_overhead(
        service_cost_pools: Dict[str, Decimal], # {"IT": 500000, "HR": 300000, "FACILITIES": 400000}
        production_cost_centers: Dict[str, Decimal], # {"MFG_AUSTIN": 1200000, "MFG_DALLAS": 800000}
        driver_weights: Dict[str, Dict[str, Decimal]] # {"IT": {"MFG_AUSTIN": 0.6, "MFG_DALLAS": 0.4}}
    ) -> Dict[str, Any]:
        allocated_results = {k: Decimal("0.0") for k in production_cost_centers}
        audit_trail = []

        for pool_name, pool_amount in service_cost_pools.items():
            weights = driver_weights.get(pool_name, {})
            for target_center, weight in weights.items():
                if target_center in allocated_results:
                    allocated_amt = (pool_amount * weight).quantize(Decimal("0.01"))
                    allocated_results[target_center] += allocated_amt
                    audit_trail.append({
                        "from_service_pool": pool_name,
                        "to_production_center": target_center,
                        "driver_weight_pct": float(weight * 100),
                        "allocated_amount": float(allocated_amt)
                    })

        final_totals = {}
        for center, initial_direct in production_cost_centers.items():
            overhead = allocated_results.get(center, Decimal("0.0"))
            final_totals[center] = {
                "initial_direct_cost": float(initial_direct),
                "allocated_overhead": float(overhead),
                "total_fully_absorbed_cost": float(initial_direct + overhead)
            }

        return {
            "production_center_totals": final_totals,
            "allocation_audit_steps": audit_trail
        }
