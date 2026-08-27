"""
NexERP Total Rewards & Comprehensive Compensation Statement Engine.
Aggregates:
- Direct Compensation (Base Salary, Performance Bonus, Equity/Stock Grants)
- Indirect Benefits (Employer Medical/Dental/Vision Subsidies, 401(k) Match, HSA/FSA)
- Paid Leave Benefits Value (PTO, Statutory Holidays).
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class TotalRewardsStatementService:
    """
    Total Rewards & Employee Compensation Statement Service.
    """

    @classmethod
    def generate_annual_rewards_statement(
        cls,
        employee_id: str,
        employee_name: str,
        base_salary: Decimal,
        annual_bonus: Decimal,
        equity_grant_annual_value: Decimal,
        employer_health_insurance_subsidy: Decimal,
        employer_401k_match: Decimal,
        annual_pto_hours: Decimal,
        paid_holidays_count: int = 10
    ) -> Dict:
        """
        Compute total monetary value of employee compensation and benefit package.
        """
        # Value of paid leave = (Base Salary / 2080 hours) * Total Paid Leave Hours
        hourly_wage = base_salary / Decimal("2080.0")
        total_paid_leave_hours = annual_pto_hours + (Decimal(str(paid_holidays_count)) * Decimal("8.0"))
        leave_benefit_value = (hourly_wage * total_paid_leave_hours).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        direct_cash_comp = base_salary + annual_bonus + equity_grant_annual_value
        employer_benefits_total = employer_health_insurance_subsidy + employer_401k_match + leave_benefit_value
        total_rewards_value = direct_cash_comp + employer_benefits_total

        benefits_percentage = ((employer_benefits_total / direct_cash_comp) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if direct_cash_comp > Decimal("0.0") else Decimal("0.0")

        return {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "direct_compensation": {
                "base_salary": float(base_salary),
                "annual_bonus": float(annual_bonus),
                "equity_grants": float(equity_grant_annual_value),
                "total_direct_cash": float(direct_cash_comp)
            },
            "employer_paid_benefits": {
                "health_insurance_subsidy": float(employer_health_insurance_subsidy),
                "retirement_401k_match": float(employer_401k_match),
                "paid_time_off_value": float(leave_benefit_value),
                "total_benefits_value": float(employer_benefits_total)
            },
            "total_rewards_package_value": float(total_rewards_value),
            "benefits_uplift_percent": float(benefits_percentage)
        }
