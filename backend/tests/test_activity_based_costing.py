"""
NexERP Activity-Based Costing Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.analytics.services import ActivityBasedCostingService


def test_abc_product_overhead_assignment():
    """
    Verify ABC overhead assignment:
    Activity Pool 1: Machine Setups - $120,000 / 600 hours = $200/hr
    Activity Pool 2: Quality Inspections - $60,000 / 1200 inspections = $50/inspection

    PROD-A: 2.0 setup_hrs + 1.0 inspection -> overhead = $400 + $50 = $450/unit
    PROD-B: 0.5 setup_hrs + 3.0 inspections -> overhead = $100 + $150 = $250/unit
    """
    pools = [
        {
            "activity_name": "Machine Setup",
            "driver_name": "setup_hours",
            "total_pool_cost": Decimal("120000.0"),
            "total_driver_volume": Decimal("600.0")
        },
        {
            "activity_name": "Quality Inspection",
            "driver_name": "inspections",
            "total_pool_cost": Decimal("60000.0"),
            "total_driver_volume": Decimal("1200.0")
        }
    ]

    product_matrix = {
        "PROD-A": {"setup_hours": Decimal("2.0"), "inspections": Decimal("1.0")},
        "PROD-B": {"setup_hours": Decimal("0.5"), "inspections": Decimal("3.0")}
    }

    res = ActivityBasedCostingService.calculate_abc_product_cost(pools, product_matrix)

    assert res["product_abc_overhead"]["PROD-A"]["total_abc_overhead_per_unit"] == 450.0
    assert res["product_abc_overhead"]["PROD-B"]["total_abc_overhead_per_unit"] == 250.0
    assert len(res["activity_pools"]) == 2
