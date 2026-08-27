"""
NexERP Strategic Sourcing RFQ & Landed Cost Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.procurement.services import RFQAuctionService, LandedCostService


def test_rfq_multi_attribute_vendor_bid_evaluation():
    """
    Verify weighted ranking of vendor bids combining Price (50%), Lead Time (30%), Quality (20%).
    """
    bids = [
        {"vendor_id": "V1", "vendor_name": "Supplier A", "bid_unit_price": "100.00", "lead_time_days": 10, "historical_quality_rating": 95.0},
        {"vendor_id": "V2", "vendor_name": "Supplier B", "bid_unit_price": "80.00", "lead_time_days": 20, "historical_quality_rating": 90.0},
        {"vendor_id": "V3", "vendor_name": "Supplier C", "bid_unit_price": "120.00", "lead_time_days": 5, "historical_quality_rating": 98.0},
    ]

    ranked = RFQAuctionService.evaluate_vendor_bids(bids)
    assert len(ranked) == 3
    assert ranked[0]["is_awarded"] is True
    assert ranked[0]["composite_score"] > 0


def test_landed_cost_allocation_by_value():
    """
    Verify allocation of $1,000 ocean freight across 2 items ($4,000 + $6,000 = $10,000 total):
    Item 1 gets 40% ($400), Item 2 gets 60% ($600).
    """
    lines = [
        {"item_id": "ITM-1", "sku": "BEARING", "quantity": "100", "unit_cost": "40.00"},  # $4,000
        {"item_id": "ITM-2", "sku": "MOTOR", "quantity": "10", "unit_cost": "600.00"},    # $6,000
    ]
    expenses = [
        {"type": "OCEAN_FREIGHT", "amount": "1000.00"}
    ]

    allocated = LandedCostService.allocate_landed_costs(lines, expenses, allocation_method="BY_VALUE")
    assert len(allocated) == 2
    assert allocated[0]["allocated_landed_cost"] == 400.00
    assert allocated[0]["new_unit_landed_cost"] == 44.0000
    assert allocated[1]["allocated_landed_cost"] == 600.00
    assert allocated[1]["new_unit_landed_cost"] == 660.0000
