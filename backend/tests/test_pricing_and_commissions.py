"""
NexERP Commercial Pricing & Sales Commission Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.sales.services import PricingEngineService, CommissionEngineService


def test_tiered_volume_discount_matrix_calculation():
    """
    Verify tiered volume pricing:
    Base: $100.
    1-9 units: $100
    10-49 units: 10% discount ($90)
    50+ units: 20% discount ($80)
    """
    volume_breaks = [
        {"min_quantity": 10, "discount_percent": 10.0},
        {"min_quantity": 50, "discount_percent": 20.0},
    ]

    p_1 = PricingEngineService.calculate_effective_price(
        base_list_price=Decimal("100.00"),
        order_quantity=Decimal("5.0"),
        customer_tier="STANDARD",
        volume_breaks=volume_breaks
    )
    assert p_1["effective_unit_price"] == 100.00

    p_20 = PricingEngineService.calculate_effective_price(
        base_list_price=Decimal("100.00"),
        order_quantity=Decimal("20.0"),
        customer_tier="STANDARD",
        volume_breaks=volume_breaks
    )
    assert p_20["effective_unit_price"] == 90.00
    assert p_20["total_order_amount"] == 1800.00

    p_60 = PricingEngineService.calculate_effective_price(
        base_list_price=Decimal("100.00"),
        order_quantity=Decimal("60.0"),
        customer_tier="STANDARD",
        volume_breaks=volume_breaks
    )
    assert p_60["effective_unit_price"] == 80.00
    assert p_60["total_order_amount"] == 4800.00


def test_sales_commission_quota_accelerator():
    """
    Verify sales commission calculation with accelerator:
    Quota: $100,000, Actual: $130,000 (130% Attainment).
    Base (5% on $130,000) = $6,500.
    Bonus (Revenue > 120% = $10,000 * 5% * 1.0) = $500.
    Total = $7,000.
    """
    res = CommissionEngineService.calculate_rep_commission(
        rep_id="REP-007",
        rep_name="James Bond",
        quota_target=Decimal("100000.00"),
        actual_revenue_achieved=Decimal("130000.00"),
        base_commission_rate_percent=Decimal("5.0"),
        enable_accelerator=True
    )

    assert res["quota_attainment_percent"] == 130.00
    assert res["base_commission_amount"] == 6500.00
    assert res["total_commission_payout"] >= 7000.00
