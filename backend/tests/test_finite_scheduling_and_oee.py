"""
NexERP Finite Capacity Scheduling & Overall Equipment Effectiveness (OEE) Test Suite.
"""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from backend.src.modules.manufacturing.services import FiniteSchedulingService, OEECalculationService


def test_forward_finite_operation_scheduling():
    """
    Verify forward sequencing of routing operations:
    Op 1: Setup 30m + (10m * 2 units) = 50 mins
    Buffer: 15 mins
    Op 2: Setup 15m + (20m * 2 units) = 55 mins
    """
    ops = [
        {"sequence_number": 10, "description": "Milling", "setup_time_mins": 30.0, "run_time_mins_per_unit": 10.0, "planned_quantity": 2.0},
        {"sequence_number": 20, "description": "Assembly", "setup_time_mins": 15.0, "run_time_mins_per_unit": 20.0, "planned_quantity": 2.0},
    ]

    start = datetime(2026, 3, 1, 8, 0, tzinfo=timezone.utc)
    scheduled = FiniteSchedulingService.schedule_operations_forward(start, ops)

    assert len(scheduled) == 2
    assert scheduled[0]["total_duration_minutes"] == 50.0
    assert scheduled[1]["total_duration_minutes"] == 55.0


def test_oee_world_class_calculation():
    """
    Verify OEE computation:
    Planned: 480 mins, Downtime: 48 mins -> Availability = 432/480 = 90%
    Operating: 432 mins, Ideal 4 mins/unit * 100 units = 400 mins -> Performance = 400/432 = 92.59%
    Units: 100 total, 2 scrap -> Quality = 98/100 = 98%
    OEE = 0.90 * 0.9259 * 0.98 = ~81.66%
    """
    metrics = OEECalculationService.calculate_work_center_oee(
        planned_production_time_mins=Decimal("480.0"),
        unplanned_downtime_mins=Decimal("48.0"),
        ideal_cycle_time_mins_per_unit=Decimal("4.0"),
        total_units_produced=Decimal("100.0"),
        defective_scrap_units=Decimal("2.0")
    )

    assert metrics["availability_rate_percent"] == 90.0
    assert metrics["quality_yield_percent"] == 98.0
    assert metrics["composite_oee_percent"] > 80.0
    assert metrics["world_class_benchmark"] == "TYPICAL_GOOD"
