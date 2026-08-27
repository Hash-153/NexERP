"""
NexERP Supply Chain, Consignment, ROP & Freight Audit Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.procurement.services import (
    ConsignmentInventoryService,
    FreightAuditService,
)
from backend.src.modules.inventory.services import ReorderPointOptimizationService
from backend.src.modules.quality_control.services import SCARManagementService


def test_consignment_inventory_consumption():
    """
    Verify consumption of 150 consignment bearings @ $40 each = $6,000 settlement.
    """
    res = ConsignmentInventoryService.log_consignment_consumption(
        vendor_id="VEND-001",
        vendor_name="Apex Bearings",
        item_id="ITM-BRG-01",
        item_sku="BEARING-6205",
        consumed_quantity=Decimal("150.0"),
        agreed_consignment_unit_price=Decimal("40.00"),
        work_order_id="WO-1002"
    )

    assert res["consumed_quantity"] == 150.0
    assert res["total_settlement_payable"] == 6000.00
    assert res["status"] == "SETTLEMENT_PENDING"


def test_stochastic_reorder_point_and_eoq():
    """
    Verify safety stock and Wilson EOQ formulas.
    """
    rop_res = ReorderPointOptimizationService.calculate_stochastic_rop(
        avg_daily_demand=Decimal("50.0"),
        daily_demand_std_dev=Decimal("5.0"),
        avg_lead_time_days=Decimal("9.0"),
        lead_time_std_dev_days=Decimal("0.0"),
        target_service_level_percent=95.0
    )
    # Lead time demand = 50 * 9 = 450.
    # sigma_ddlt = sqrt(9 * 25) = 15.
    # Safety stock = 1.645 * 15 = 24.68.
    # ROP = 450 + 24.68 = 474.68.
    assert rop_res["lead_time_demand"] == 450.0
    assert rop_res["safety_stock_units"] == 24.68
    assert rop_res["reorder_point_rop_units"] == 474.68

    eoq_res = ReorderPointOptimizationService.calculate_economic_order_quantity(
        annual_demand_units=Decimal("10000.0"),
        fixed_order_cost_usd=Decimal("50.00"),
        annual_holding_cost_per_unit_usd=Decimal("4.00")
    )
    # EOQ = sqrt(2 * 10000 * 50 / 4) = sqrt(250,000) = 500 units.
    assert eoq_res["economic_order_quantity_eoq"] == 500.0


def test_freight_bill_three_way_audit():
    """
    Verify carrier invoice verification and overcharge detection.
    """
    res = FreightAuditService.audit_carrier_invoice(
        carrier_invoice_number="INV-CARRIER-881",
        bol_tracking_number="BOL-99120",
        invoiced_linehaul=Decimal("1200.00"),
        invoiced_fuel_surcharge=Decimal("200.00"),
        invoiced_accessorials=Decimal("150.00"),
        contracted_linehaul=Decimal("1000.00"),
        contracted_fuel_surcharge=Decimal("200.00"),
        contracted_accessorials=Decimal("50.00")
    )

    # Invoiced = $1550, Contracted = $1250, Overcharge = $300.
    assert res["total_invoiced_amount"] == 1550.00
    assert res["total_contracted_amount"] == 1250.00
    assert res["total_overcharge_amount"] == 300.00
    assert res["is_audit_approved"] is False
    assert res["audit_disposition"] == "REJECTED_OVERCHARGE_DISPUTED"


def test_scar_supplier_notice_issuance():
    """
    Verify SCAR notice issuance and 14-day 8D response deadline.
    """
    res = SCARManagementService.issue_scar_notice(
        scar_number="SCAR-2026-004",
        vendor_id="V-102",
        vendor_name="Vanguard Metals",
        item_sku="SHAFT-STEEL-20MM",
        grn_number="GRN-8812",
        defect_description="Thread pitch out of tolerance on 40 units",
        defect_quantity=40,
        severity_level="MAJOR",
        response_window_days=14
    )

    assert res["scar_number"] == "SCAR-2026-004"
    assert res["status"] == "PENDING_SUPPLIER_8D"
    assert res["scorecard_penalty_points"] == 5
