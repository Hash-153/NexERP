"""
NexERP Benefits Administration & Project EVM Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.human_resources.services import BenefitsAdministrationService
from backend.src.modules.projects.services import EarnedValueService, ProjectRevenueRecognitionService


def test_401k_tiered_employer_matching():
    """
    Verify 401(k) safe-harbor match:
    Gross: $10,000, EE Deferral: 5%.
    Tier 1 (100% on first 3%) = $300.
    Tier 2 (50% on next 2%) = $100.
    Total ER Match = $400.
    """
    res = BenefitsAdministrationService.calculate_401k_employer_match(
        gross_salary=Decimal("10000.00"),
        employee_deferral_percent=Decimal("5.0")
    )

    assert res["employee_contribution_amount"] == 500.00
    assert res["employer_tier1_match_amount"] == 300.00
    assert res["employer_tier2_match_amount"] == 100.00
    assert res["employer_total_matching_contribution"] == 400.00


def test_earned_value_management_project_metrics():
    """
    Verify EVM indices:
    BAC: $100,000.
    Planned: 50% ($50,000 PV).
    Actual Work Done: 60% ($60,000 EV).
    Actual Cost Incurred: $50,000 (AC).
    CV = $60k - $50k = +$10k (Under Budget).
    SV = $60k - $50k = +$10k (Ahead of Schedule).
    CPI = 60/50 = 1.20.
    SPI = 60/50 = 1.20.
    """
    metrics = EarnedValueService.calculate_project_evm_metrics(
        budget_at_completion=Decimal("100000.00"),
        percent_work_completed=Decimal("60.0"),
        planned_percent_at_date=Decimal("50.0"),
        actual_cost_incurred=Decimal("50000.00")
    )

    assert metrics["planned_value_pv"] == 50000.00
    assert metrics["earned_value_ev"] == 60000.00
    assert metrics["cost_variance_cv"] == 10000.00
    assert metrics["schedule_variance_sv"] == 10000.00
    assert metrics["cost_performance_index_cpi"] == 1.2000
    assert metrics["cost_status"] == "UNDER_BUDGET"
    assert metrics["schedule_status"] == "AHEAD_OF_SCHEDULE"


def test_asc_606_percentage_of_completion_revenue_recognition():
    """
    Verify ASC 606 PoC revenue recognition:
    Contract: $500,000, Total Budget Cost: $400,000.
    Incurred: $100,000 (25% complete).
    Earned Revenue: $125,000.
    Previously recognized: $0 -> Current period to recognize: $125,000.
    """
    poc = ProjectRevenueRecognitionService.calculate_poc_revenue_recognition(
        total_contract_value=Decimal("500000.00"),
        total_estimated_budget_cost=Decimal("400000.00"),
        cumulative_incurred_cost=Decimal("100000.00"),
        previously_recognized_revenue=Decimal("0.0")
    )

    assert poc["percentage_of_completion_percent"] == 25.00
    assert poc["cumulative_earned_revenue"] == 125000.00
    assert poc["current_period_revenue_to_recognize"] == 125000.00
