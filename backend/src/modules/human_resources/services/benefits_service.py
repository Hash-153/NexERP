"""
NexERP Employee Benefits Administration & Deduction Engine.
Manages pre-tax and post-tax benefit deductions:
- Employer 401(k) matching formulas (e.g. 100% on first 3%, 50% on next 2%)
- Healthcare plans (High Deductible + HSA, PPO, HMO)
- Section 125 Cafeteria Plan FSA elections.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class BenefitsAdministrationService:
    """
    Employee Benefits & Retirement Plan Calculation Service.
    """

    @classmethod
    def calculate_401k_employer_match(
        cls,
        gross_salary: Decimal,
        employee_deferral_percent: Decimal,
        first_tier_match_percent: Decimal = Decimal("100.0"),
        first_tier_cap_percent: Decimal = Decimal("3.0"),
        second_tier_match_percent: Decimal = Decimal("50.0"),
        second_tier_cap_percent: Decimal = Decimal("2.0")
    ) -> Dict:
        """
        Calculate employee 401(k) pre-tax contribution and company matching funds using tiered safe-harbor formula.
        """
        ee_contribution = (gross_salary * (employee_deferral_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Tier 1 Match (100% on first 3%)
        tier1_ee_pct = min(employee_deferral_percent, first_tier_cap_percent)
        tier1_match = (gross_salary * (tier1_ee_pct / Decimal("100.0")) * (first_tier_match_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Tier 2 Match (50% on next 2%)
        tier2_ee_pct = max(Decimal("0.0"), min(employee_deferral_percent - first_tier_cap_percent, second_tier_cap_percent))
        tier2_match = (gross_salary * (tier2_ee_pct / Decimal("100.0")) * (second_tier_match_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        er_total_match = tier1_match + tier2_match

        return {
            "gross_salary": float(gross_salary),
            "employee_deferral_percent": float(employee_deferral_percent),
            "employee_contribution_amount": float(ee_contribution),
            "employer_tier1_match_amount": float(tier1_match),
            "employer_tier2_match_amount": float(tier2_match),
            "employer_total_matching_contribution": float(er_total_match),
            "total_retirement_funding": float(ee_contribution + er_total_match)
        }

    @classmethod
    def calculate_health_insurance_premium_split(
        cls,
        tier: str = "EMPLOYEE_PLUS_FAMILY",
        plan_type: str = "HDHP_HSA",
        employer_subsidy_percent: Decimal = Decimal("75.0")
    ) -> Dict:
        """
        Calculate monthly health insurance premium split between employee payroll deduction and employer benefit cost.
        """
        # Monthly Base Premium Rates
        premium_matrix = {
            "EMPLOYEE_ONLY": Decimal("650.00"),
            "EMPLOYEE_PLUS_SPOUSE": Decimal("1300.00"),
            "EMPLOYEE_PLUS_CHILDREN": Decimal("1150.00"),
            "EMPLOYEE_PLUS_FAMILY": Decimal("1850.00"),
        }

        total_premium = premium_matrix.get(tier.upper(), Decimal("650.00"))
        er_share = (total_premium * (employer_subsidy_percent / Decimal("100.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        ee_payroll_deduction = total_premium - er_share

        return {
            "coverage_tier": tier,
            "plan_type": plan_type,
            "total_monthly_premium": float(total_premium),
            "employer_subsidy_percent": float(employer_subsidy_percent),
            "employer_company_cost": float(er_share),
            "employee_payroll_deduction": float(ee_payroll_deduction)
        }
