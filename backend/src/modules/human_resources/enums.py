"""
NexERP Human Resources & Payroll Enums.
"""

from enum import Enum


class EmploymentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ON_LEAVE = "ON_LEAVE"
    TERMINATED = "TERMINATED"


class AttendanceStatus(str, Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    HALF_DAY = "HALF_DAY"


class LeaveStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class PayrollStatus(str, Enum):
    DRAFT = "DRAFT"
    CALCULATED = "CALCULATED"
    APPROVED = "APPROVED"
    PAID = "PAID"


class ExpenseClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REIMBURSED = "REIMBURSED"
    REJECTED = "REJECTED"
