"""
NexERP AP/AR Matching, Dynamic Discounts, NACHA ACH, Aging & Dunning Test Suite.
"""

from datetime import date
from decimal import Decimal
import pytest

from backend.src.modules.accounts_payable.services import (
    ThreeWayMatchService,
    EarlyPaymentDiscountService,
    NACHAPaymentFileService
)
from backend.src.modules.accounts_receivable.services import (
    ARAgingAnalysisService,
    CustomerCreditScoringService,
    DunningEscalationService
)


def test_three_way_match_line_tolerance_verification():
    """
    Verify 3-way match:
    PO: 100 units @ $50.00.
    GRN: 100 units accepted.
    Bill: 100 units @ $50.00 -> MATCHED.
    """
    po_lines = [{"item_id": "ITM-101", "unit_price": "50.00", "quantity_ordered": "100"}]
    grn_lines = [{"item_id": "ITM-101", "quantity_accepted": "100"}]
    bill_lines = [{"item_id": "ITM-101", "unit_price": "50.00", "quantity": "100"}]

    res = ThreeWayMatchService.verify_three_way_match(po_lines, grn_lines, bill_lines)
    assert res["is_matched"] is True
    assert res["overall_status"] == "AUTO_APPROVED_MATCHED"


def test_early_payment_terms_and_apr_yield():
    """
    Verify 2/10 Net 30 terms:
    Invoice: $10,000.
    Discount 2% = $200. Net payment = $9,800.
    Implied APR = [2 / 98] * [365 / 20] * 100 = ~37.24% APR!
    """
    res = EarlyPaymentDiscountService.calculate_early_payment_terms(
        invoice_amount=Decimal("10000.00"),
        invoice_date=date(2026, 1, 1),
        discount_percent=Decimal("2.0"),
        discount_days=10,
        net_due_days=30
    )

    assert res["discount_savings_amount"] == 200.00
    assert res["net_discounted_payment_amount"] == 9800.00
    assert res["annualized_rate_of_return_apr_percent"] > 35.0
    assert res["recommendation"] == "TAKE_DISCOUNT_HIGH_YIELD"


def test_nacha_ach_file_generation_formatting():
    """
    Verify NACHA 94-character fixed line format generation.
    """
    payments = [
        {
            "vendor_id": "VEND-001",
            "vendor_name": "Acme Steel Corp",
            "vendor_bank_routing": "121000358",
            "vendor_bank_account": "987654321",
            "amount": "15420.50",
            "settlement_date": date(2026, 2, 1)
        }
    ]

    nacha_text = NACHAPaymentFileService.generate_nacha_ach_file(
        immediate_destination_routing="121000358",
        immediate_origin_company_id="1234567890",
        company_name="Apex Dynamics",
        company_discretionary_data="AP-DISBURSEMENT",
        payments=payments
    )

    lines = nacha_text.split("\n")
    assert len(lines) >= 4
    for line in lines:
        assert len(line) == 94


def test_ar_cecl_aging_buckets_and_loss_reserves():
    """
    Verify AR aging bucket classification and CECL doubtful account provision calculation.
    """
    invoices = [
        {"invoice_number": "INV-101", "customer_name": "Client A", "due_date": date(2026, 1, 20), "open_balance": "10000.00"},  # 11 days overdue (Current 0-30)
        {"invoice_number": "INV-102", "customer_name": "Client B", "due_date": date(2025, 12, 1), "open_balance": "5000.00"},   # 61 days overdue (Past Due 61-90)
    ]

    as_of = date(2026, 1, 31)
    res = ARAgingAnalysisService.calculate_ar_aging_and_provisions(invoices, as_of)

    assert res["total_ar_outstanding"] == 15000.00
    assert res["total_cecl_bad_debt_reserve"] > 0
    assert res["aging_buckets"]["CURRENT_0_30"]["total_amount"] == 10000.00
    assert res["aging_buckets"]["PAST_DUE_61_90"]["total_amount"] == 5000.00


def test_dunning_level_and_statutory_interest():
    """
    Verify Dunning Level 3 (Urgent Demand & Credit Hold) when 45 days overdue.
    """
    res = DunningEscalationService.evaluate_dunning_level(
        invoice_number="INV-8801",
        customer_name="Late Payer Inc",
        principal_amount=Decimal("10000.00"),
        due_date=date(2025, 12, 1),
        as_of_date=date(2026, 1, 15)
    )

    assert res["days_overdue"] == 45
    assert res["dunning_level"] == 3
    assert res["statutory_action"] == "CREDIT_HOLD_ENFORCED"
    assert res["accrued_interest_penalty"] > 0
