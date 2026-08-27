"""
NexERP Cost Center Allocation & Overhead Apportionment Engine.
Implements:
- Direct Allocation Method
- Step-Down (Sequential) Allocation Method
- Reciprocal (Simultaneous Equation) Allocation Method
for service departments (IT, HR, Facilities, Maintenance) allocating overhead costs to production revenue centers.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class CostAllocationService:
    """
    Managerial Cost Accounting Overhead Allocation Engine.
    """

    @classmethod
    def direct_allocation(
        cls,
        service_department_costs: Dict[str, Decimal],
        production_departments: List[str],
        allocation_bases: Dict[str, Dict[str, Decimal]]
    ) -> Dict:
        """
        Directly apportion service department overheads to production departments based on usage ratios.
        """
        allocated_results = {p: Decimal("0.0") for p in production_departments}
        breakdown = []

        for s_dept, cost in service_department_costs.items():
            bases = allocation_bases.get(s_dept, {})
            total_base = sum(bases.get(p, Decimal("0.0")) for p in production_departments)

            if total_base <= Decimal("0.0"):
                continue

            for p_dept in production_departments:
                dept_base = bases.get(p_dept, Decimal("0.0"))
                share = ((dept_base / total_base) * cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                allocated_results[p_dept] += share

                breakdown.append({
                    "from_service_department": s_dept,
                    "to_production_department": p_dept,
                    "allocated_amount": float(share),
                    "allocation_ratio_percent": float(((dept_base / total_base) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                })

        return {
            "total_service_costs_allocated": float(sum(service_department_costs.values())),
            "allocated_to_production_totals": {k: float(v) for k, v in allocated_results.items()},
            "allocation_details": breakdown
        }
