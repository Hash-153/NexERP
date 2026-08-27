"""
NexERP Rough-Cut Capacity Planning (RCCP) & MPS Feasibility Engine.
Calculates:
- Work Center Required Load (Hours) = MPS Planned Units * Unit Standard Machine/Labor Hours
- Available Work Center Capacity (Hours) = Shifts * Shift_Hours * Work_Centers * Efficiency
- Capacity Utilization % & Overload / Underload bottleneck alerts across weekly time buckets.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class RoughCutCapacityService:
    """
    Master Production Schedule (MPS) Rough-Cut Capacity Planning Service.
    """

    @classmethod
    def evaluate_rccp_feasibility(
        cls,
        mps_schedule: List[Dict],
        work_center_capacities: Dict[str, Decimal],
        bill_of_resources: Dict[str, Dict[str, Decimal]]
    ) -> Dict:
        """
        Evaluate weekly machine and labor load requirements against nominal available capacities.
        """
        # work_center_capacities: {"WC-CNC": Decimal("80.0"), "WC-ASSY": Decimal("120.0")}
        # bill_of_resources: {"ITEM-PUMP": {"WC-CNC": Decimal("1.5"), "WC-ASSY": Decimal("2.0")}}
        # mps_schedule: [{"week": 1, "item_id": "ITEM-PUMP", "planned_quantity": Decimal("40.0")}]

        weekly_loads = {}
        overloaded_buckets = []

        for mps_item in mps_schedule:
            week_num = mps_item.get("week", 1)
            item_id = mps_item["item_id"]
            qty = Decimal(str(mps_item["planned_quantity"]))

            if week_num not in weekly_loads:
                weekly_loads[week_num] = {wc: Decimal("0.0") for wc in work_center_capacities.keys()}

            resources = bill_of_resources.get(item_id, {})
            for wc, hrs_per_unit in resources.items():
                if wc in weekly_loads[week_num]:
                    weekly_loads[week_num][wc] += (qty * hrs_per_unit).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        summary_by_week = []
        for week_num, loads in sorted(weekly_loads.items(), key=lambda x: x[0]):
            wc_summaries = {}
            for wc, req_hours in loads.items():
                avail_hours = work_center_capacities.get(wc, Decimal("1.0"))
                util_pct = ((req_hours / avail_hours) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if avail_hours > Decimal("0.0") else Decimal("0.0")
                is_overloaded = req_hours > avail_hours

                if is_overloaded:
                    overloaded_buckets.append({"week": week_num, "work_center": wc, "overload_hours": float(req_hours - avail_hours), "utilization": float(util_pct)})

                wc_summaries[wc] = {
                    "required_hours": float(req_hours),
                    "available_capacity_hours": float(avail_hours),
                    "utilization_percent": float(util_pct),
                    "is_overloaded": is_overloaded
                }

            summary_by_week.append({
                "week": week_num,
                "work_center_loads": wc_summaries
            })

        return {
            "total_weeks_evaluated": len(weekly_loads),
            "is_plan_feasible": len(overloaded_buckets) == 0,
            "overloaded_bottlenecks_count": len(overloaded_buckets),
            "overloaded_bottlenecks": overloaded_buckets,
            "weekly_capacity_schedule": summary_by_week
        }
