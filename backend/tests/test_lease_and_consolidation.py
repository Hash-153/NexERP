"""
NexERP Lease Accounting, Consolidation, Impairment, and Cost Allocation Test Suite.
"""

from datetime import date
from decimal import Decimal
import pytest

from backend.src.modules.financials.services import (
    LeaseAccountingService,
    ConsolidationEliminationService,
    AssetImpairmentService,
    CostAllocationService,
)


def test_asc_842_lease_schedule_and_classification():
    """
    Verify ASC 842:
    Monthly Payment: $5,000, 36 months, 6% annual discount rate.
    Classification: Operating Lease vs Finance Lease.
    """
    classification = LeaseAccountingService.classify_lease(
        lease_term_months=36,
        asset_economic_life_months=60,
        present_value_payments=Decimal("164478.00"),
        fair_value_underlying_asset=Decimal("200000.00"),
        has_ownership_transfer=False
    )
    assert classification == "OPERATING_LEASE"

    schedule_res = LeaseAccountingService.calculate_lease_schedule(
        monthly_payment=Decimal("5000.00"),
        lease_term_months=36,
        annual_discount_rate_percent=Decimal("6.0"),
        start_date=date(2026, 1, 1)
    )

    assert len(schedule_res["schedule"]) == 36
    assert schedule_res["initial_lease_liability"] > 0.0
    # Final balance may have small rounding residual due to floating-point arithmetic
    assert schedule_res["schedule"][-1]["ending_lease_liability"] < 1.0


def test_intercompany_elimination_journal_generation():
    """
    Verify intercompany trade AP/AR elimination voucher generation.
    """
    ic_balances = [
        {"transaction_type": "TRADE_AR_AP", "amount": "45000.00", "from_entity_name": "NexERP US", "to_entity_name": "NexERP UK"},
        {"transaction_type": "INTERCOMPANY_SALES", "amount": "120000.00", "from_entity_name": "NexERP US", "to_entity_name": "NexERP UK"}
    ]

    res = ConsolidationEliminationService.generate_elimination_entries(ic_balances)
    assert res["total_elimination_count"] == 2
    assert res["total_eliminated_ar_ap_amount"] == 45000.00
    assert res["total_eliminated_revenue_amount"] == 120000.00


def test_fixed_asset_impairment_ias36():
    """
    Carrying Value: $100,000.
    FVLCD: $80,000.
    Value in Use: $85,000.
    Recoverable Amount = Max(80k, 85k) = $85,000.
    Impairment Loss = $100,000 - $85,000 = $15,000.
    """
    res = AssetImpairmentService.evaluate_impairment(
        carrying_book_value=Decimal("100000.00"),
        fair_value_less_costs_to_sell=Decimal("80000.00"),
        discounted_value_in_use=Decimal("85000.00")
    )

    assert res["recoverable_amount"] == 85000.00
    assert res["is_impaired"] is True
    assert res["impairment_loss_amount"] == 15000.00
    assert res["adjusted_carrying_value"] == 85000.00


def test_service_department_direct_cost_allocation():
    """
    IT Department ($100,000) allocated to Assembly (60%) and Machining (40%).
    """
    service_costs = {"IT_DEPT": Decimal("100000.00")}
    prod_depts = ["MACHINING", "ASSEMBLY"]
    bases = {"IT_DEPT": {"MACHINING": Decimal("40.0"), "ASSEMBLY": Decimal("60.0")}}

    res = CostAllocationService.direct_allocation(service_costs, prod_depts, bases)
    assert res["allocated_to_production_totals"]["MACHINING"] == 40000.00
    assert res["allocated_to_production_totals"]["ASSEMBLY"] == 60000.00
