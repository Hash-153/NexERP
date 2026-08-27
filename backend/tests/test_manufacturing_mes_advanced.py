"""
NexERP Advanced MES, RCCP, Yield Variance, Subcontracting & Tooling Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.manufacturing.services import (
    RoughCutCapacityService,
    ScrapVarianceService,
    SubcontractingService,
    ToolingLifeManagementService,
)


def test_rccp_feasibility_and_overload_detection():
    """
    Verify RCCP load vs capacity.
    WC-CNC capacity: 40 hrs.
    MPS Week 1: 50 units @ 1.0 hr/unit = 50 hrs (10 hrs overload).
    """
    mps = [{"week": 1, "item_id": "ITEM-HOUSING", "planned_quantity": Decimal("50.0")}]
    capacities = {"WC-CNC": Decimal("40.0")}
    bor = {"ITEM-HOUSING": {"WC-CNC": Decimal("1.0")}}

    res = RoughCutCapacityService.evaluate_rccp_feasibility(mps, capacities, bor)
    assert res["is_plan_feasible"] is False
    assert res["overloaded_bottlenecks_count"] == 1
    assert res["overloaded_bottlenecks"][0]["overload_hours"] == 10.0


def test_material_scrap_and_yield_variance_accounting():
    """
    Verify scrap variance:
    Input: 1,000 units. Standard scrap allowance: 5% (50 units).
    Actual scrap: 80 units (30 units excess scrap).
    Standard cost: $10.00 / unit -> Unfavorable Scrap Variance = $300.00.
    """
    res = ScrapVarianceService.calculate_job_scrap_variance(
        production_order_number="PO-2026-009",
        item_sku="ALUM-PLATE-10MM",
        total_input_units=Decimal("1000.0"),
        standard_scrap_percent=Decimal("5.0"),
        actual_scrap_units=Decimal("80.0"),
        standard_unit_cost=Decimal("10.00")
    )

    assert res["standard_scrap_allowed_units"] == 50.0
    assert res["actual_scrap_units"] == 80.0
    assert res["scrap_variance_units"] == 30.0
    assert res["scrap_variance_cost_usd"] == 300.00
    assert res["variance_type"] == "UNFAVORABLE"


def test_outside_processing_subcontracting_cost_capitalization():
    """
    Verify subcontract job:
    100 units raw shaft ($50/unit) sent for Anodizing ($15/unit service) + $200 freight.
    Total = $5,000 material + $1,500 service + $200 freight = $6,700 ($67.00/unit).
    """
    res = SubcontractingService.calculate_subcontract_job_cost(
        subcontract_po_number="SUB-PO-441",
        supplier_id="V-COAT-01",
        supplier_name="Superior Anodizing Inc",
        parent_item_sku="RAW-SHAFT",
        processed_item_sku="ANODIZED-SHAFT",
        quantity_sent_to_subcontractor=Decimal("100.0"),
        unit_service_charge=Decimal("15.00"),
        parent_material_unit_cost=Decimal("50.00"),
        freight_handling_charge=Decimal("200.00")
    )

    assert res["parent_material_cost_total"] == 5000.00
    assert res["subcontract_service_cost_total"] == 1500.00
    assert res["total_capitalized_finished_cost"] == 6700.00
    assert res["new_unit_cost"] == 67.00


def test_tooling_wear_and_sharpening_life():
    """
    Verify stamping die maintenance status.
    Lifetime rated: 500,000 shots. Cumulative run: 120,000 shots.
    Shots since last sharpening: 52,000 (interval: 50,000).
    Result: Maintenance sharpening is DUE.
    """
    res = ToolingLifeManagementService.evaluate_tool_wear_status(
        tool_id="TOOL-DIE-01",
        tool_name="Progressive Stamping Die 2mm",
        tool_type="STAMPING_DIE",
        total_lifetime_shots_rated=500000,
        cumulative_shots_run=120000,
        shots_since_last_sharpening=52000,
        sharpening_interval_shots=50000
    )

    assert res["tool_wear_percent"] == 24.0
    assert res["is_sharpening_due"] is True
    assert res["tool_status"] == "SHARPENING_MAINTENANCE_DUE"
