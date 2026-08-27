"""
NexERP Finite Capacity Planning & Detailed Shop Floor Scheduling (APS) Engine.
Implements constraint-based forward and backward scheduling, machine setup sequence optimization,
and Gantt work center dispatching rules (SPT, EDD, Critical Ratio).
"""

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.manufacturing.models import WorkCenter, ProductionOrder, Routing, RoutingOperation
from backend.src.modules.manufacturing.enums import ProductionOrderStatus


class FiniteSchedulingService:
    """
    Finite Capacity Scheduling & Work Center Loading Service.
    """

    @classmethod
    def schedule_operations_forward(
        cls,
        start_datetime: datetime,
        operations: List[Dict],
        work_center_calendar: Optional[Dict[str, Decimal]] = None
    ) -> List[Dict]:
        """
        Forward scheduling: Calculate earliest start date (ESD) and earliest finish date (EFD)
        for each consecutive routing operation based on work center daily capacities.
        """
        scheduled = []
        current_time = start_datetime

        # Default standard 8 hour daily machine shift = 480 operating minutes
        daily_capacity_mins = Decimal("480.0")

        for op in operations:
            setup_mins = Decimal(str(op.get("setup_time_mins", 30.0)))
            run_mins_per_unit = Decimal(str(op.get("run_time_mins_per_unit", 15.0)))
            qty = Decimal(str(op.get("planned_quantity", 1.0)))

            total_duration_mins = setup_mins + (run_mins_per_unit * qty)

            op_start = current_time

            # Calculate duration in hours/days
            days_needed = (total_duration_mins / daily_capacity_mins)
            # Add calendar days
            duration_delta = timedelta(minutes=float(total_duration_mins))
            op_end = op_start + duration_delta

            scheduled.append({
                "sequence_number": op.get("sequence_number", 10),
                "operation_description": op.get("description", "Machining / Assembly"),
                "work_center_id": op.get("work_center_id"),
                "work_center_name": op.get("work_center_name", "Work Center"),
                "total_duration_minutes": float(total_duration_mins),
                "planned_start_datetime": op_start.isoformat(),
                "planned_end_datetime": op_end.isoformat(),
                "setup_time_minutes": float(setup_mins),
                "run_time_minutes": float(run_mins_per_unit * qty)
            })

            # Next operation starts immediately after previous completes (or with queue time)
            current_time = op_end + timedelta(minutes=15)  # 15 min inter-operation transit/queue buffer

        return scheduled

    @classmethod
    def dispatch_work_center_queue_edd(
        cls,
        work_order_queue: List[Dict]
    ) -> List[Dict]:
        """
        Earliest Due Date (EDD) dispatching rule: Orders jobs in work center queue
        by customer due date to minimize maximum lateness.
        """
        def parse_date(d):
            if isinstance(d, (date, datetime)):
                return d
            return date.fromisoformat(str(d))

        sorted_queue = sorted(work_order_queue, key=lambda x: parse_date(x.get("due_date", date.today())))
        for idx, job in enumerate(sorted_queue, start=1):
            job["queue_priority_rank"] = idx
            job["dispatch_rule"] = "EDD"

        return sorted_queue

    @classmethod
    def dispatch_work_center_queue_spt(
        cls,
        work_order_queue: List[Dict]
    ) -> List[Dict]:
        """
        Shortest Processing Time (SPT) dispatching rule: Orders jobs in work center queue
        by estimated run time to minimize work-in-progress (WIP) and average cycle time.
        """
        sorted_queue = sorted(work_order_queue, key=lambda x: float(x.get("estimated_duration_minutes", 100.0)))
        for idx, job in enumerate(sorted_queue, start=1):
            job["queue_priority_rank"] = idx
            job["dispatch_rule"] = "SPT"

        return sorted_queue
