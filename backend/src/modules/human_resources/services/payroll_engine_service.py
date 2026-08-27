"""
NexERP Progressive Tax Bracket & Monthly Payroll Calculation Engine.
Calculates marginal income tax brackets, statutory deductions (FICA/Pension), itemizes employee payslips,
and generates automated double-entry General Ledger payroll expense vouchers.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.core.events import publish_domain_event, DomainEvent, EVENT_PAYROLL_FINALIZED
from backend.src.modules.human_resources.models import (
    Employee,
    PayrollRun,
    Payslip,
    PayslipLine
)
from backend.src.modules.human_resources.schemas import PayrollRunCreate
from backend.src.modules.human_resources.enums import PayrollStatus, EmploymentStatus
from backend.src.modules.financials.models import Account, FiscalPeriod
from backend.src.modules.financials.services import GeneralLedgerService
from backend.src.modules.financials.schemas import JournalEntryCreate, JournalEntryLineCreate


class PayrollCalculationService:
    """
    Enterprise Payroll Calculation Engine.
    """

    # Progressive Marginal Income Tax Brackets (Annualized baseline converted to monthly)
    # Monthly brackets:
    # 0 - $1,000 : 10%
    # $1,000 - $3,500 : 12%
    # $3,500 - $7,500 : 22%
    # $7,500 - $15,000 : 24%
    # Above $15,000 : 32%
    TAX_SLABS = [
        (Decimal("1000.0"), Decimal("0.10")),
        (Decimal("3500.0"), Decimal("0.12")),
        (Decimal("7500.0"), Decimal("0.22")),
        (Decimal("15000.0"), Decimal("0.24")),
        (Decimal("999999999.0"), Decimal("0.32")),
    ]

    # Statutory Deductions
    FICA_SOCIAL_SECURITY_RATE = Decimal("0.0620")  # 6.2%
    MEDICARE_RATE = Decimal("0.0145")              # 1.45%
    RETIREMENT_401K_RATE = Decimal("0.0500")       # 5.0%

    @classmethod
    def calculate_progressive_income_tax(cls, taxable_gross: Decimal) -> Decimal:
        """
        Calculate progressive marginal bracket income tax withholding.
        """
        if taxable_gross <= Decimal("0.0"):
            return Decimal("0.0")

        tax_total = Decimal("0.0")
        previous_limit = Decimal("0.0")

        for limit, rate in cls.TAX_SLABS:
            if taxable_gross > previous_limit:
                taxable_in_slab = min(taxable_gross - previous_limit, limit - previous_limit)
                tax_total += taxable_in_slab * rate
                previous_limit = limit
            else:
                break

        return tax_total.quantize(Decimal("0.01"))

    @classmethod
    async def execute_payroll_run(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: PayrollRunCreate,
        user_id: Optional[str] = None
    ) -> PayrollRun:
        """
        Execute full organization payroll run:
        - Compute base, allowances, deductions, and tax withholdings per employee
        - Generate itemized payslips
        - Post balanced GL voucher (Debit Salaries Expense, Credit Tax/Benefits/Payroll Payable)
        """
        run_num = f"PAYROLL-{payload.year}-{payload.month:02d}"

        # Fetch active employees
        emp_query = select(Employee).where(
            Employee.tenant_id == tenant_id,
            Employee.employment_status == EmploymentStatus.ACTIVE.value,
            Employee.is_deleted == False
        )
        emp_res = await db.execute(emp_query)
        employees = emp_res.scalars().all()

        if not employees:
            raise BusinessRuleViolationError("No active employees found for payroll processing.")

        payroll_run = PayrollRun(
            tenant_id=tenant_id,
            run_number=run_num,
            month=payload.month,
            year=payload.year,
            run_date=payload.run_date,
            status=PayrollStatus.CALCULATED.value
        )
        db.add(payroll_run)
        await db.flush()

        tot_gross = Decimal("0.0")
        tot_ded = Decimal("0.0")
        tot_tax = Decimal("0.0")
        tot_net = Decimal("0.0")

        for emp in employees:
            base = emp.base_salary
            # Standard Allowances: Housing (15% of base), Transport (5% of base)
            housing_allowance = (base * Decimal("0.15")).quantize(Decimal("0.01"))
            transport_allowance = (base * Decimal("0.05")).quantize(Decimal("0.01"))
            gross_pay = base + housing_allowance + transport_allowance

            # Progressive Income Tax
            income_tax = cls.calculate_progressive_income_tax(gross_pay)

            # Deductions
            social_sec = (gross_pay * cls.FICA_SOCIAL_SECURITY_RATE).quantize(Decimal("0.01"))
            medicare = (gross_pay * cls.MEDICARE_RATE).quantize(Decimal("0.01"))
            retirement = (base * cls.RETIREMENT_401K_RATE).quantize(Decimal("0.01"))
            other_deductions = social_sec + medicare + retirement

            total_employee_deductions = income_tax + other_deductions
            net_pay = gross_pay - total_employee_deductions

            tot_gross += gross_pay
            tot_tax += income_tax
            tot_ded += other_deductions
            tot_net += net_pay

            payslip_num = f"PS-{payload.year}{payload.month:02d}-{emp.employee_number}"

            payslip = Payslip(
                tenant_id=tenant_id,
                payroll_run_id=payroll_run.id,
                employee_id=emp.id,
                payslip_number=payslip_num,
                base_salary=base,
                gross_pay=gross_pay,
                total_deductions=total_employee_deductions,
                income_tax_withheld=income_tax,
                net_pay=net_pay,
                status="GENERATED"
            )
            db.add(payslip)
            await db.flush()

            # Itemized lines
            lines_data = [
                ("Base Salary", "EARNING", base),
                ("Housing Allowance", "EARNING", housing_allowance),
                ("Transport Allowance", "EARNING", transport_allowance),
                ("Income Tax Withholding", "TAX", income_tax),
                ("Social Security (FICA)", "DEDUCTION", social_sec),
                ("Medicare", "DEDUCTION", medicare),
                ("Retirement 401(k) / Pension", "DEDUCTION", retirement),
            ]
            for comp_name, comp_type, amt in lines_data:
                p_line = PayslipLine(
                    tenant_id=tenant_id,
                    payslip_id=payslip.id,
                    component_name=comp_name,
                    component_type=comp_type,
                    amount=amt
                )
                db.add(p_line)

        payroll_run.total_gross_pay = tot_gross
        payroll_run.total_deductions = tot_ded
        payroll_run.total_tax_withheld = tot_tax
        payroll_run.total_net_pay = tot_net

        # Generate & Post General Ledger Journal Entry
        # Find Open Fiscal Period
        p_res = await db.execute(select(FiscalPeriod).where(FiscalPeriod.tenant_id == tenant_id, FiscalPeriod.is_locked == False).limit(1))
        period = p_res.scalar_one_or_none()

        if period:
            # Lookup Accounts
            sal_acc = (await db.execute(select(Account).where(Account.tenant_id == tenant_id, Account.classification == "SALARIES_AND_WAGES").limit(1))).scalars().first()
            tax_pay_acc = (await db.execute(select(Account).where(Account.tenant_id == tenant_id, Account.classification == "TAX_PAYABLE").limit(1))).scalars().first()
            pay_pay_acc = (await db.execute(select(Account).where(Account.tenant_id == tenant_id, Account.classification == "PAYROLL_PAYABLE").limit(1))).scalars().first()

            if sal_acc and tax_pay_acc and pay_pay_acc:
                gl_lines = [
                    # Debit Total Gross Salaries Expense
                    JournalEntryLineCreate(
                        account_id=sal_acc.id,
                        debit=tot_gross,
                        credit=Decimal("0.0"),
                        description=f"Gross Payroll Expense for {run_num}"
                    ),
                    # Credit Tax Withholding Liability
                    JournalEntryLineCreate(
                        account_id=tax_pay_acc.id,
                        debit=Decimal("0.0"),
                        credit=tot_tax,
                        description=f"Payroll Income Tax Withholding for {run_num}"
                    ),
                    # Credit Net Payroll & Benefits Payable Liability
                    JournalEntryLineCreate(
                        account_id=pay_pay_acc.id,
                        debit=Decimal("0.0"),
                        credit=tot_ded + tot_net,
                        description=f"Net Salaries & Benefits Payable for {run_num}"
                    )
                ]

                jv_payload = JournalEntryCreate(
                    entry_date=payload.run_date,
                    period_id=period.id,
                    currency="USD",
                    exchange_rate=Decimal("1.0"),
                    reference=run_num,
                    narration=f"Monthly Payroll Accrual for {run_num}",
                    source_document_type="PayrollRun",
                    source_document_id=payroll_run.id,
                    lines=gl_lines
                )
                jv = await GeneralLedgerService.create_journal_entry(db, tenant_id, jv_payload, user_id)
                posted_jv = await GeneralLedgerService.post_journal_entry(db, tenant_id, jv.id, user_id)
                payroll_run.journal_entry_id = posted_jv.id

        payroll_run.status = PayrollStatus.APPROVED.value
        await db.commit()
        await db.refresh(payroll_run)

        # Dispatch event
        await publish_domain_event(DomainEvent(
            event_name=EVENT_PAYROLL_FINALIZED,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            payload={"run_id": payroll_run.id, "run_number": payroll_run.run_number, "net_pay": float(payroll_run.total_net_pay)}
        ))

        return payroll_run

    @classmethod
    async def list_payroll_runs(cls, db: AsyncSession, tenant_id: str) -> List[PayrollRun]:
        query = (
            select(PayrollRun)
            .where(PayrollRun.tenant_id == tenant_id)
            .options(selectinload(PayrollRun.payslips).selectinload(Payslip.lines))
            .order_by(PayrollRun.year.desc(), PayrollRun.month.desc())
        )
        res = await db.execute(query)
        return list(res.scalars().all())
