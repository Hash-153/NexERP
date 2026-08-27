"""
NexERP Transportation (TMS), Customs Tariffs, and Cross-Docking Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.procurement.services import CarrierRatingService, CustomsTariffService
from backend.src.modules.inventory.services import CrossDockingService


def test_tms_carrier_freight_rating():
    """
    Verify freight calculation:
    LTL: 1,500 lbs (15 CWT @ $14.50 = $217.50) + 400 miles ($140.00) = $357.50 Base.
    Liftgate: $75.00.
    Fuel Surcharge: 16% on $357.50 = $57.20.
    Total = $489.70.
    """
    res = CarrierRatingService.rate_freight_shipment(
        origin_zip="60601",
        destination_zip="48201",
        total_weight_lbs=Decimal("1500.0"),
        distance_miles=Decimal("400.0"),
        is_ftl=False,
        national_diesel_price=Decimal("3.65"),
        require_liftgate=True
    )

    assert res["service_mode"] == "LESS_THAN_TRUCKLOAD_LTL"
    assert res["base_linehaul_charge"] == 357.50
    assert res["accessorial_charges_total"] == 75.00
    assert res["fuel_surcharge_amount"] == 57.20
    assert res["total_estimated_freight_charge"] == 489.70


def test_customs_harmonized_tariff_calculation():
    """
    Verify customs duty for Ball Bearings (HTS 8482.10.50 @ 9.0% duty):
    Declared Value: $100,000 from DE (Germany).
    Base Duty = $9,000.
    MPF Fee (0.3464% = $346.40).
    Total = $9,346.40.
    """
    res = CustomsTariffService.calculate_customs_duties(
        hts_code="8482.10.50",
        customs_declared_value_usd=Decimal("100000.00"),
        origin_country_code="DE"
    )

    assert res["base_duty_amount_usd"] == 9000.00
    assert res["merchandise_processing_fee_mpf"] == 346.40
    assert res["total_customs_duty_payable"] == 9346.40


def test_cross_dock_allocation_to_backorders():
    """
    Verify direct flow-through allocation of 80 inbound motors across 2 pending customer backorders:
    Backorder 1: 50 units (HIGH priority).
    Backorder 2: 40 units (NORMAL priority).
    Result: BO 1 receives 50 (satisfied), BO 2 receives 30 (10 remaining), 0 putaway excess.
    """
    backorders = [
        {"sales_order_id": "SO-1", "sales_order_number": "SO-101", "customer_name": "Acme", "quantity_unfulfilled": 50, "priority": "HIGH", "order_date": "2026-01-10"},
        {"sales_order_id": "SO-2", "sales_order_number": "SO-102", "customer_name": "Beta", "quantity_unfulfilled": 40, "priority": "NORMAL", "order_date": "2026-01-12"},
    ]

    res = CrossDockingService.match_inbound_shipment_to_backorders(
        inbound_item_id="ITM-MOTOR",
        inbound_sku="ELEC-MOTOR-15KW",
        inbound_quantity_received=Decimal("80.0"),
        pending_sales_backorders=backorders
    )

    assert res["total_inbound_quantity"] == 80.0
    assert res["cross_docked_quantity"] == 80.0
    assert res["excess_quantity_for_warehouse_putaway"] == 0.0
    assert res["allocations"][0]["allocated_quantity"] == 50.0
    assert res["allocations"][0]["is_fully_satisfied"] is True
    assert res["allocations"][1]["allocated_quantity"] == 30.0
    assert res["allocations"][1]["is_fully_satisfied"] is False
