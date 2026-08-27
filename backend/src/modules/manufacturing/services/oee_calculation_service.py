"""
NexERP Overall Equipment Effectiveness (OEE) & Total Productive Maintenance (TPM) Engine.
Calculates World-Class OEE benchmark metrics:
OEE = Availability Rate x Performance Efficiency x Quality Yield Rate.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.manufacturing.models import WorkCenter


class OEECalculationService:
    """
    Manufacturing Shop Floor OEE & Asset Utilization Analytics Service.
    """

    @classmethod
    def calculate_work_center_oee(
        cls,
        planned_production_time_mins: Decimal,
        unplanned_downtime_mins: Decimal,
        ideal_cycle_time_mins_per_unit: Decimal,
        total_units_produced: Decimal,
        defective_scrap_units: Decimal
    ) -> Dict:
        """
        Compute standard 3-pillar OEE metric according to SEMI E10 / ISO 22400.
        """
        if planned_production_time_mins <= Decimal("0.0"):
            return {
                "availability_rate_percent": 0.0,
                "performance_efficiency_percent": 0.0,
                "quality_yield_percent": 0.0,
                "composite_oee_percent": 0.0,
                "world_class_benchmark": "BELOW_TARGET"
            }

        # 1. Availability = Operating Time / Planned Production Time
        operating_time_mins = max(Decimal("0.0"), planned_production_time_mins - unplanned_downtime_mins)
        availability_rate = (operating_time_mins / planned_production_time_mins).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # 2. Performance = (Ideal Cycle Time * Total Units Produced) / Operating Time
        if operating_time_mins > Decimal("0.0"):
            net_operating_time = ideal_cycle_time_mins_per_unit * total_units_produced
            performance_rate = min(Decimal("1.0"), (net_operating_time / operating_time_mins).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))
        else:
            performance_rate = Decimal("0.0")

        # 3. Quality = Good Units Produced / Total Units Produced
        good_units = max(Decimal("0.0"), total_units_produced - defective_scrap_units)
        if total_units_produced > Decimal("0.0"):
            quality_rate = (good_units / total_units_produced).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        else:
            quality_rate = Decimal("1.0")

        # Composite OEE
        composite_oee = (availability_rate * performance_rate * quality_rate * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # World Class Manufacturing (WCM) benchmark standard is >= 85.0%
        if composite_oee >= Decimal("85.0"):
            benchmark = "WORLD_CLASS"
        elif composite_oee >= Decimal("70.0"):
            benchmark = "TYPICAL_GOOD"
        elif composite_oee >= Decimal("55.0"):
            benchmark = "NEEDS_IMPROVEMENT"
        else:
            benchmark = "CRITICAL_ACTION_REQUIRED"

        return {
            "planned_time_minutes": float(planned_production_time_mins),
            "operating_time_minutes": float(operating_time_mins),
            "downtime_minutes": float(unplanned_downtime_mins),
            "total_units_produced": float(total_units_produced),
            "good_units_produced": float(good_units),
            "scrap_units": float(defective_scrap_units),
            "availability_rate_percent": float((availability_rate * Decimal("100.0")).quantize(Decimal("0.01"))),
            "performance_efficiency_percent": float((performance_rate * Decimal("100.0")).quantize(Decimal("0.01"))),
            "quality_yield_percent": float((quality_rate * Decimal("100.0")).quantize(Decimal("0.01"))),
            "composite_oee_percent": float(composite_oee),
            "world_class_benchmark": benchmark
        }
