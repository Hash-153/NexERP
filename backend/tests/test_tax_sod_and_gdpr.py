"""
NexERP Multi-State Tax, Total Rewards, 9-Box Talent, SoD Conflicts & GDPR Test Suite.
"""

from decimal import Decimal
import pytest

from backend.src.modules.human_resources.services import (
    MultiStateTaxService,
    TotalRewardsStatementService,
    SuccessionPlanningService,
)
from backend.src.modules.governance.services import (
    SoDConflictAnalyzerService,
    GDPRAErasureService,
)


def test_multi_state_reciprocal_tax_withholding():
    """
    Verify IL resident working in WI has tax withheld for IL under reciprocal agreement.
    """
    res = MultiStateTaxService.calculate_state_withholding(
        gross_pay=Decimal("5000.00"),
        resident_state="IL",
        work_state="WI"
    )

    assert res["has_reciprocity_agreement"] is True
    assert res["primary_taxing_state"] == "IL"
    assert res["state_tax_rate_percent"] == 4.95
    assert res["state_tax_withholding_amount"] == 247.50


def test_total_rewards_statement_breakdown():
    """
    Verify total rewards:
    Base: $120,000 + Bonus: $15,000 + Benefits: $18,000 + PTO Value.
    """
    res = TotalRewardsStatementService.generate_annual_rewards_statement(
        employee_id="EE-100",
        employee_name="Sarah Connor",
        base_salary=Decimal("120000.00"),
        annual_bonus=Decimal("15000.00"),
        equity_grant_annual_value=Decimal("10000.00"),
        employer_health_insurance_subsidy=Decimal("12000.00"),
        employer_401k_match=Decimal("6000.00"),
        annual_pto_hours=Decimal("160.0"),
        paid_holidays_count=10
    )

    assert res["direct_compensation"]["total_direct_cash"] == 145000.00
    assert res["total_rewards_package_value"] > 165000.00


def test_succession_planning_9_box_star():
    """
    Verify (3,3) Performance/Potential maps to 'STAR' high-priority successor.
    """
    res = SuccessionPlanningService.evaluate_employee_talent_position(
        employee_id="EE-201",
        employee_name="James T. Kirk",
        current_job_title="Operations Lead",
        performance_score_1_to_3=3,
        potential_score_1_to_3=3
    )

    assert res["nine_box_classification"] == "STAR"
    assert res["is_high_flight_risk_asset"] is True


def test_sod_toxic_permission_conflict_detection():
    """
    Verify detection of AP invoice creation + AP payment release toxic conflict.
    """
    perms = ["AP_INVOICE_CREATE", "AP_PAYMENT_RELEASE", "VIEW_REPORTS"]
    res = SoDConflictAnalyzerService.audit_user_role_privileges(
        user_id="U-991",
        username="john.rogers",
        assigned_permissions=perms
    )

    assert res["is_sod_compliant"] is False
    assert res["detected_conflicts_count"] == 1
    assert res["detected_conflicts"][0]["rule_code"] == "SOD-FIN-01"
    assert res["detected_conflicts"][0]["risk_level"] == "CRITICAL"


def test_gdpr_pii_erasure_and_anonymization():
    """
    Verify customer PII anonymization preserving ledger audit identity.
    """
    res = GDPRAErasureService.anonymize_customer_pii(
        customer_id="CUST-4412",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@personal-domain.com",
        phone_number="555-019-2834",
        billing_address="123 Private Oak Lane, Apt 4B, Chicago, IL"
    )

    assert res["gdpr_compliance_status"] == "ERASURE_COMPLETED"
    assert res["anonymized_record"]["first_name"] == "REDACTED_GDPR"
    assert "erased_" in res["anonymized_record"]["email"]
    assert res["anonymized_record"]["phone_number"] == "000-000-0000"
