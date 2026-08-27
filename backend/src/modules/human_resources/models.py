"""
NexERP Human Resource Management (HRM) & Progressive Payroll Database Models.
Handles Employee Master, Departments, Attendance, Leave Balances, Progressive Tax Bracket Payroll, and Expense Claims.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Department(Base):
    """
    Organizational business unit or cost center.
    """
    __tablename__ = "hr_departments"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    manager_id = Column(String(36), nullable=True)
    cost_center_id = Column(String(36), nullable=True)

    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")


class JobPosition(Base):
    """
    Job role and title within enterprise structure.
    """
    __tablename__ = "hr_job_positions"

    code = Column(String(50), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    department_id = Column(String(36), ForeignKey("hr_departments.id"), nullable=False)
    grade_level = Column(String(20), default="L3", nullable=False)

    department = relationship("Department")


class Employee(Base):
    """
    Employee Master record with compensation, reporting hierarchy, and banking profile.
    """
    __tablename__ = "hr_employees"

    employee_number = Column(String(50), nullable=False, index=True, doc="e.g. 'EMP-00101'")
    user_id = Column(String(36), ForeignKey("auth_users.id"), nullable=True, unique=True)
    
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    
    date_of_birth = Column(Date, nullable=True)
    date_of_joining = Column(Date, nullable=False)
    
    department_id = Column(String(36), ForeignKey("hr_departments.id"), nullable=False)
    job_position_id = Column(String(36), ForeignKey("hr_job_positions.id"), nullable=False)
    reports_to_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    
    employment_status = Column(String(30), default="ACTIVE", nullable=False, doc="ACTIVE, ON_LEAVE, TERMINATED")
    national_tax_id = Column(String(50), nullable=True, doc="SSN / National Tax Identifier")
    bank_account_number = Column(String(100), nullable=True)
    bank_name = Column(String(100), nullable=True)
    
    base_salary = Column(Numeric(18, 4), default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    department = relationship("Department", foreign_keys=[department_id])
    job_position = relationship("JobPosition")
    leaves = relationship("LeaveRequest", back_populates="employee")
    payslips = relationship("Payslip", back_populates="employee")
    expense_claims = relationship("ExpenseClaim", back_populates="employee")

    __table_args__ = (
        Index("ix_hr_emp_tenant_number", "tenant_id", "employee_number", unique=True),
    )


class AttendanceLog(Base):
    """
    Daily attendance punch record.
    """
    __tablename__ = "hr_attendance_logs"

    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False, index=True)
    punch_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    hours_worked = Column(Numeric(5, 2), default=8.0, nullable=False)
    overtime_hours = Column(Numeric(5, 2), default=0.0, nullable=False)
    status = Column(String(30), default="PRESENT", nullable=False, doc="PRESENT, ABSENT, LATE, HALF_DAY")

    employee = relationship("Employee")


class LeaveType(Base):
    """
    Leave classification and annual entitlement rules.
    """
    __tablename__ = "hr_leave_types"

    code = Column(String(30), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    annual_allowance_days = Column(Numeric(5, 2), default=20.0, nullable=False)
    is_carry_forward = Column(Boolean, default=True, nullable=False)
    max_carry_forward_days = Column(Numeric(5, 2), default=5.0, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)


class LeaveRequest(Base):
    """
    Employee leave application and manager sign-off ticket.
    """
    __tablename__ = "hr_leave_requests"

    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False, index=True)
    leave_type_id = Column(String(36), ForeignKey("hr_leave_types.id"), nullable=False)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Numeric(5, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    
    status = Column(String(30), default="SUBMITTED", nullable=False, doc="SUBMITTED, APPROVED, REJECTED, CANCELLED")
    approved_by_id = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    employee = relationship("Employee", back_populates="leaves")
    leave_type = relationship("LeaveType")


class PayrollRun(Base):
    """
    Monthly enterprise payroll batch run.
    """
    __tablename__ = "hr_payroll_runs"

    run_number = Column(String(50), nullable=False, index=True, doc="e.g. 'PAYROLL-2026-01'")
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    run_date = Column(Date, nullable=False)
    
    total_gross_pay = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_deductions = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_tax_withheld = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_net_pay = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, doc="DRAFT, CALCULATED, APPROVED, PAID")
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)

    payslips = relationship("Payslip", back_populates="payroll_run", cascade="all, delete-orphan")


class Payslip(Base):
    """
    Individual employee monthly payslip with earnings, deductions, and tax withholdings.
    """
    __tablename__ = "hr_payslips"

    payroll_run_id = Column(String(36), ForeignKey("hr_payroll_runs.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False)
    payslip_number = Column(String(50), nullable=False, index=True)
    
    base_salary = Column(Numeric(18, 4), nullable=False)
    gross_pay = Column(Numeric(18, 4), nullable=False)
    total_deductions = Column(Numeric(18, 4), nullable=False)
    income_tax_withheld = Column(Numeric(18, 4), nullable=False)
    net_pay = Column(Numeric(18, 4), nullable=False)
    status = Column(String(30), default="GENERATED", nullable=False)

    payroll_run = relationship("PayrollRun", back_populates="payslips")
    employee = relationship("Employee", back_populates="payslips")
    lines = relationship("PayslipLine", back_populates="payslip", cascade="all, delete-orphan")


class PayslipLine(Base):
    """
    Itemized allowance or deduction line item on payslip.
    """
    __tablename__ = "hr_payslip_lines"

    payslip_id = Column(String(36), ForeignKey("hr_payslips.id", ondelete="CASCADE"), nullable=False)
    component_name = Column(String(100), nullable=False)
    component_type = Column(String(30), nullable=False, doc="EARNING, DEDUCTION, TAX")
    amount = Column(Numeric(18, 4), nullable=False)

    payslip = relationship("Payslip", back_populates="lines")


class ExpenseClaim(Base):
    """
    Employee travel and business expense reimbursement voucher.
    """
    __tablename__ = "hr_expense_claims"

    claim_number = Column(String(50), nullable=False, index=True, doc="e.g. 'EXP-2026-0001'")
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False)
    claim_date = Column(Date, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="SUBMITTED", nullable=False, doc="SUBMITTED, APPROVED, REIMBURSED, REJECTED")
    
    approved_by_id = Column(String(36), nullable=True)
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)

    employee = relationship("Employee", back_populates="expense_claims")
    lines = relationship("ExpenseClaimLine", back_populates="claim", cascade="all, delete-orphan")


class ExpenseClaimLine(Base):
    """
    Individual receipt line item in employee expense claim.
    """
    __tablename__ = "hr_expense_claim_lines"

    expense_claim_id = Column(String(36), ForeignKey("hr_expense_claims.id", ondelete="CASCADE"), nullable=False)
    expense_date = Column(Date, nullable=False)
    category = Column(String(100), nullable=False, doc="Travel, Lodging, Meals, Software, Supplies")
    description = Column(String(255), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    expense_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True)

    claim = relationship("ExpenseClaim", back_populates="lines")
