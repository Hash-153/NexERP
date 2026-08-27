"""
NexERP Human Resources & Progressive Payroll Test Suite.
Tests Marginal Tax Slabs, Statutory Deductions, and General Ledger Payroll Accruals.
"""

from datetime import date
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.modules.human_resources.models import Department, JobPosition, Employee
from backend.src.modules.human_resources.services import PayrollCalculationService
from backend.src.modules.human_resources.schemas import PayrollRunCreate
from backend.src.modules.financials.models import Account, FiscalYear, FiscalPeriod
from backend.src.modules.financials.services import FiscalPeriodService
from backend.src.modules.financials.schemas import FiscalYearCreate


def test_progressive_tax_bracket_calculation():
    """
    Test progressive marginal tax calculation across multiple income slabs:
    - Tier 1: $1,000 gross -> 10% = $100
    - Tier 2: $3,000 gross -> ($1,000 * 0.10) + ($2,000 * 0.12) = 100 + 240 = $340
    - Tier 3: $5,000 gross -> ($1,000 * 0.10) + ($2,500 * 0.12) + ($1,500 * 0.22) = 100 + 300 + 330 = $730
    """
    tax_1k = PayrollCalculationService.calculate_progressive_income_tax(Decimal("1000.00"))
    assert tax_1k == Decimal("100.00")

    tax_3k = PayrollCalculationService.calculate_progressive_income_tax(Decimal("3000.00"))
    assert tax_3k == Decimal("340.00")

    tax_5k = PayrollCalculationService.calculate_progressive_income_tax(Decimal("5000.00"))
    assert tax_5k == Decimal("730.00")


@pytest.mark.asyncio
async def test_full_payroll_run_execution_and_gl_accrual(db_session: AsyncSession):
    """
    Execute monthly payroll for employees and verify payslip generation and GL voucher creation.
    """
    tenant_id = "org_corp_hq_001"

    # Setup GL Accounts
    sal_acc = Account(tenant_id=tenant_id, code="60100", name="Salaries", account_type="EXPENSE", classification="SALARIES_AND_WAGES")
    tax_acc = Account(tenant_id=tenant_id, code="22100", name="Tax Withheld", account_type="LIABILITY", classification="TAX_PAYABLE")
    pay_acc = Account(tenant_id=tenant_id, code="22000", name="Payroll Payable", account_type="LIABILITY", classification="PAYROLL_PAYABLE")
    db_session.add_all([sal_acc, tax_acc, pay_acc])
    await db_session.flush()

    fy = await FiscalPeriodService.create_fiscal_year_with_12_periods(
        db_session, tenant_id, FiscalYearCreate(name="FY 2026", start_date=date(2026, 1, 1), end_date=date(2026, 12, 31))
    )

    # Setup Department, Position, and Employee
    dept = Department(tenant_id=tenant_id, code="ENG", name="Engineering")
    db_session.add(dept)
    await db_session.flush()

    pos = JobPosition(tenant_id=tenant_id, code="ENG-01", title="Engineer", department_id=dept.id)
    db_session.add(pos)
    await db_session.flush()

    emp = Employee(
        tenant_id=tenant_id,
        employee_number="EMP-101",
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@example.com",
        date_of_joining=date(2025, 1, 1),
        department_id=dept.id,
        job_position_id=pos.id,
        base_salary=Decimal("5000.00"),
        employment_status="ACTIVE"
    )
    db_session.add(emp)
    await db_session.commit()

    # Execute Payroll Run
    run = await PayrollCalculationService.execute_payroll_run(
        db_session,
        tenant_id,
        PayrollRunCreate(month=1, year=2026, run_date=date(2026, 1, 31)),
        user_id="test_cfo"
    )

    assert run.status == "APPROVED"
    assert run.total_gross_pay > Decimal("5000.00")  # Base + housing (15%) + transport (5%) = 6,000
    assert run.total_net_pay > Decimal("0.0")
    assert run.journal_entry_id is not None
