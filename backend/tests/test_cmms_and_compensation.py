"""
NexERP Plant Maintenance CMMS, Downtime Pareto, Compensation, and FMLA/PTO Test Suite.
"""

from datetime import date
from decimal import Decimal
import pytest

from backend.src.modules.manufacturing.services import DowntimeParetoService, MaintenanceWorkOrderService
from backend.src.modules.human_resources.services import CompensationAnalyticsService, FMLALeaveAccrualService


def test_downtime_pareto_distribution():
    """
    Verify 80/20 Pareto distribution on machine stoppage events.
    """
    events = [
        {"reason_category": "MECHANICAL_BREAKDOWN", "duration_minutes": 240},
        {"reason_category": "TOOLING_CHANGEOVER", "duration_minutes": 120},
        {"reason_category": "MATERIAL_SHORTAGE", "duration_minutes": 30},
        {"reason_category": "SENSOR_JAM", "duration_minutes": 10},
    ]

    res = DowntimeParetoService.analyze_downtime_pareto(events)
    assert res["total_downtime_minutes"] == 400.0
    assert res["top_failure_cause"] == "MECHANICAL_BREAKDOWN"
    assert res["pareto_distribution"][0]["percentage_of_total"] == 60.0


def test_maintenance_work_order_meter_trigger():
    """
    Verify PM trigger when machine meter hours exceed 500-hour service interval.
    """
    res = MaintenanceWorkOrderService.evaluate_pm_schedule_trigger(
        machine_id="M-CNC-01",
        machine_name="Haas 5-Axis CNC Mill",
        current_meter_hours=Decimal("1520.0"),
        last_pm_meter_hours=Decimal("1000.0"),
        meter_interval_hours=Decimal("500.0")
    )

    assert res["is_maintenance_required"] is True
    assert res["hours_since_last_pm"] == 520.0
    assert res["trigger_reason"] == "METER_HOURS_EXCEEDED"


def test_compensation_compa_ratio_and_merit_increase():
    """
    Verify Compa-Ratio:
    Actual Salary: $100,000, Grade Midpoint: $100,000 -> Compa-Ratio = 100% (Mid Quartile).
    Performance: 'EXCEEDS_EXPECTATIONS' -> 5.5% merit increase ($5,500).
    """
    ratio_res = CompensationAnalyticsService.calculate_employee_compa_ratio(
        actual_salary=Decimal("100000.00"),
        grade_min=Decimal("80000.00"),
        grade_mid=Decimal("100000.00"),
        grade_max=Decimal("120000.00")
    )
    assert ratio_res["compa_ratio_percent"] == 100.00
    assert ratio_res["quartile"] == "MID_QUARTILE"

    merit_res = CompensationAnalyticsService.recommend_merit_increase(
        current_salary=Decimal("100000.00"),
        performance_rating="EXCEEDS_EXPECTATIONS",
        grade_mid=Decimal("100000.00")
    )
    assert merit_res["recommended_increase_percent"] == 5.50
    assert merit_res["annual_increase_amount"] == 5500.00
    assert merit_res["new_base_salary"] == 105500.00


def test_fmla_rolling_entitlement_and_pto_accrual():
    """
    Verify FMLA 12-month rolling lookback entitlement and tenure PTO accrual.
    """
    leaves = [
        {"start_date": date(2025, 6, 1), "hours_taken": 80},
        {"start_date": date(2025, 10, 1), "hours_taken": 40},
    ]

    fmla_res = FMLALeaveAccrualService.calculate_fmla_rolling_entitlement(
        as_of_date=date(2026, 1, 31),
        past_12_month_fmla_leaves=leaves
    )
    assert fmla_res["hours_used_in_12mo_window"] == 120.0
    assert fmla_res["hours_remaining_available"] == 360.0
    assert fmla_res["weeks_remaining"] == 9.0

    pto_res = FMLALeaveAccrualService.calculate_periodic_pto_accrual(
        years_of_service=4,  # 3-5 years tier: 160 hrs/year
        current_accrued_balance=Decimal("50.0"),
        pay_periods_per_year=24
    )
    assert pto_res["annual_pto_allotment_hours"] == 160.0
    assert pto_res["accrual_per_pay_period"] == 6.67
    assert pto_res["new_pto_balance"] == 56.67
