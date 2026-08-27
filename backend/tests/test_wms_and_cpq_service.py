"""
NexERP Directed Putaway, GS1 Parser, CPQ, Rebates & Field Service Test Suite.
"""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from backend.src.modules.inventory.services import (
    DirectedPutawayService,
    DockSchedulingService,
    GS1BarcodeParserService,
)
from backend.src.modules.sales.services import (
    CPQRulesEngineService,
    CustomerRebatesService,
    FieldServiceDispatchService,
)


def test_directed_putaway_velocity_and_capacity_matching():
    """
    Verify directed putaway assigns fast mover to Zone A matching weight and volume.
    """
    bins = [
        {"id": "BIN-A1", "bin_code": "01-01-A", "zone": "GENERAL", "velocity_tier": "A", "max_weight_capacity_kg": 2000.0, "max_volume_capacity_m3": 10.0, "current_weight_kg": 0.0, "current_volume_m3": 0.0},
        {"id": "BIN-C4", "bin_code": "04-01-C", "zone": "GENERAL", "velocity_tier": "C", "max_weight_capacity_kg": 2000.0, "max_volume_capacity_m3": 10.0, "current_weight_kg": 0.0, "current_volume_m3": 0.0},
    ]

    res = DirectedPutawayService.recommend_putaway_location(
        item_sku="FAST-MOVER-SKU",
        item_velocity_class="A",
        weight_per_unit_kg=Decimal("10.0"),
        volume_per_unit_m3=Decimal("0.05"),
        quantity=Decimal("50.0"),
        is_hazmat=False,
        available_bins=bins
    )

    assert res["putaway_feasible"] is True
    assert res["recommended_bin"]["bin_code"] == "01-01-A"
    assert res["recommended_bin"]["velocity_tier"] == "A"


def test_gs1_128_barcode_parser():
    """
    Verify extraction of GTIN, Lot, Expiration Date, and Serial Number.
    """
    raw_code = "(01)00850012345678(17)261231(10)LOT-8891(21)SN-44120"
    res = GS1BarcodeParserService.parse_gs1_barcode(raw_code)

    assert res["is_valid_gs1"] is True
    assert res["gtin_01"] == "00850012345678"
    assert res["expiration_date_17"] == "2026-12-31"
    assert res["lot_number_10"] == "LOT-8891"
    assert res["serial_number_21"] == "SN-44120"


def test_cpq_rules_engine_validation():
    """
    Verify CPQ validation: Selecting 500kW Motor without Heavy-Duty Inverter triggers missing co-requisite violation.
    """
    price_table = {
        "MOTOR_500KW": Decimal("8500.00"),
        "INVERTER_HD_HEAVY_DUTY": Decimal("3200.00")
    }

    invalid_res = CPQRulesEngineService.validate_configuration(
        base_product_sku="DRIVE-SYS-BASE",
        base_price=Decimal("15000.00"),
        selected_features=["MOTOR_500KW"],
        feature_price_table=price_table
    )
    assert invalid_res["is_configuration_valid"] is False
    assert invalid_res["configuration_violations"][0]["violation_type"] == "MISSING_CO_REQUISITE"

    valid_res = CPQRulesEngineService.validate_configuration(
        base_product_sku="DRIVE-SYS-BASE",
        base_price=Decimal("15000.00"),
        selected_features=["MOTOR_500KW", "INVERTER_HD_HEAVY_DUTY"],
        feature_price_table=price_table
    )
    assert valid_res["is_configuration_valid"] is True
    assert valid_res["total_configured_quote_price"] == 26700.00


def test_customer_volume_rebate_accrual():
    """
    Verify 4% rebate tier earned on $150,000 annual qualifying spend = $6,000 rebate.
    """
    res = CustomerRebatesService.calculate_earned_rebate(
        customer_id="CUST-009",
        customer_name="Global Aviation Dynamics",
        annual_qualifying_spend_usd=Decimal("150000.00")
    )

    assert res["earned_rebate_percent"] == 4.0
    assert res["rebate_credit_memo_amount"] == 6000.00
    assert res["is_rebate_eligible"] is True


def test_field_service_sla_dispatch():
    """
    Verify Gold Tier 8-hour SLA deadline calculation.
    """
    now = datetime(2026, 2, 27, 9, 0, 0, tzinfo=timezone.utc)
    res = FieldServiceDispatchService.dispatch_service_ticket(
        ticket_id="SRV-2026-881",
        customer_name="Starlight Medical",
        service_address="100 Medical Center Dr",
        sla_tier="GOLD",
        created_at=now,
        technician_id="TECH-104",
        technician_name="David Miller",
        estimated_labor_hours=Decimal("4.0")
    )

    assert res["sla_tier"] == "GOLD"
    assert res["sla_window_hours"] == 8
    assert res["total_estimated_labor_cost"] == 500.00
