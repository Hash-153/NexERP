"""
NexERP Fixed Asset Multi-Method Depreciation Schedule Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.financials.services import FixedAssetService


def test_straight_line_depreciation_schedule_accuracy():
    """
    Verify straight line depreciation: Cost $120,000, Salvage $20,000, 5 Years.
    Depreciable base = $100,000 ($20,000/year, $1,666.67/month).
    """
    schedule = FixedAssetService.calculate_depreciation_schedule(
        acquisition_cost=Decimal("120000.00"),
        salvage_value=Decimal("20000.00"),
        useful_life_years=5,
        depreciation_method="STRAIGHT_LINE"
    )

    assert len(schedule) == 5
    assert schedule[0]["depreciation_expense"] == 20000.00
    assert schedule[4]["ending_book_value"] == 20000.00
    assert schedule[4]["accumulated_depreciation"] == 100000.00


def test_double_declining_balance_schedule_accuracy():
    """
    Verify double declining balance (200% DDB): Cost $10,000, Salvage $1,000, 5 Years (Rate = 40%).
    Year 1: $10,000 * 0.40 = $4,000
    Year 2: $6,000 * 0.40 = $2,400
    """
    schedule = FixedAssetService.calculate_depreciation_schedule(
        acquisition_cost=Decimal("10000.00"),
        salvage_value=Decimal("1000.00"),
        useful_life_years=5,
        depreciation_method="DOUBLE_DECLINING_BALANCE"
    )

    assert len(schedule) == 5
    assert schedule[0]["depreciation_expense"] == 4000.00
    assert schedule[1]["depreciation_expense"] == 2400.00
    assert schedule[4]["ending_book_value"] >= 1000.00
