"""
NexERP Human Resources & Payroll Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from .enums import EmploymentStatus, AttendanceStatus, LeaveStatus, PayrollStatus, ExpenseClaimStatus


# Department Schemas
class DepartmentBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    manager_id: Optional[str] = None
    cost_center_id: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Job Position Schemas
class JobPositionBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2, max_length=150)
    department_id: str
    grade_level: str = "L3"


class JobPositionCreate(JobPositionBase):
    pass


class JobPositionResponse(JobPositionBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Employee Schemas
class EmployeeBase(BaseModel):
    employee_number: str = Field(..., min_length=2, max_length=50)
    first_name: str = Field(..., min_length=2, max_length=100)
    last_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_joining: date
    department_id: str
    job_position_id: str
    reports_to_id: Optional[str] = None
    employment_status: EmploymentStatus = EmploymentStatus.ACTIVE
    national_tax_id: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    base_salary: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: str = "USD"


class EmployeeCreate(EmployeeBase):
    user_id: Optional[str] = None


class EmployeeUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    department_id: Optional[str] = None
    job_position_id: Optional[str] = None
    reports_to_id: Optional[str] = None
    employment_status: Optional[EmploymentStatus] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    base_salary: Optional[Decimal] = None


class EmployeeResponse(EmployeeBase):
    id: str
    tenant_id: str
    user_id: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Leave Schemas
class LeaveTypeBase(BaseModel):
    code: str
    name: str
    annual_allowance_days: Decimal = Decimal("20.0")
    is_carry_forward: bool = True
    max_carry_forward_days: Decimal = Decimal("5.0")
    is_paid: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    pass


class LeaveTypeResponse(LeaveTypeBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type_id: str
    start_date: date
    end_date: date
    total_days: Decimal = Field(..., gt=0)
    reason: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    leave_type_id: str
    start_date: date
    end_date: date
    total_days: Decimal
    reason: Optional[str]
    status: LeaveStatus
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Attendance Schemas
class AttendanceLogCreate(BaseModel):
    employee_id: str
    punch_date: date
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    hours_worked: Decimal = Decimal("8.0")
    overtime_hours: Decimal = Decimal("0.0")
    status: AttendanceStatus = AttendanceStatus.PRESENT


class AttendanceLogResponse(BaseModel):
    id: str
    tenant_id: str
    employee_id: str
    punch_date: date
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    hours_worked: Decimal
    overtime_hours: Decimal
    status: AttendanceStatus
    created_at: datetime

    class Config:
        from_attributes = True


# Payroll Schemas
class PayrollRunCreate(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2050)
    run_date: date


class PayslipLineResponse(BaseModel):
    id: str
    component_name: str
    component_type: str
    amount: Decimal

    class Config:
        from_attributes = True


class PayslipResponse(BaseModel):
    id: str
    payslip_number: str
    employee_id: str
    base_salary: Decimal
    gross_pay: Decimal
    total_deductions: Decimal
    income_tax_withheld: Decimal
    net_pay: Decimal
    status: str
    lines: List[PayslipLineResponse] = []

    class Config:
        from_attributes = True


class PayrollRunResponse(BaseModel):
    id: str
    tenant_id: str
    run_number: str
    month: int
    year: int
    run_date: date
    total_gross_pay: Decimal
    total_deductions: Decimal
    total_tax_withheld: Decimal
    total_net_pay: Decimal
    status: PayrollStatus
    journal_entry_id: Optional[str]
    payslips: List[PayslipResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Expense Claim Schemas
class ExpenseClaimLineCreate(BaseModel):
    expense_date: date
    category: str
    description: str
    amount: Decimal = Field(..., gt=0)
    expense_account_id: Optional[str] = None


class ExpenseClaimLineResponse(BaseModel):
    id: str
    expense_date: date
    category: str
    description: str
    amount: Decimal

    class Config:
        from_attributes = True


class ExpenseClaimCreate(BaseModel):
    employee_id: str
    claim_date: date
    lines: List[ExpenseClaimLineCreate] = Field(..., min_length=1)


class ExpenseClaimResponse(BaseModel):
    id: str
    tenant_id: str
    claim_number: str
    employee_id: str
    claim_date: date
    total_amount: Decimal
    status: ExpenseClaimStatus
    approved_by_id: Optional[str]
    journal_entry_id: Optional[str]
    lines: List[ExpenseClaimLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
