"""
NexERP Human Resources & Payroll Module Services.
"""

from .employee_service import EmployeeService
from .attendance_service import AttendanceService
from .leave_service import LeaveService
from .payroll_engine_service import PayrollCalculationService
from .expense_claim_service import ExpenseClaimService
from .benefits_service import BenefitsAdministrationService
from .performance_review_service import PerformanceReviewService
from .reimbursement_engine_service import ReimbursementEngineService
from .compensation_equity_service import CompensationAnalyticsService
from .fmla_leave_accrual_service import FMLALeaveAccrualService
from .multi_state_tax_service import MultiStateTaxService
from .total_rewards_service import TotalRewardsStatementService
from .succession_planning_service import SuccessionPlanningService

ExpenseReimbursementAuditService = ReimbursementEngineService

__all__ = [
    "EmployeeService",
    "AttendanceService",
    "LeaveService",
    "PayrollCalculationService",
    "ExpenseClaimService",
    "BenefitsAdministrationService",
    "PerformanceReviewService",
    "ReimbursementEngineService",
    "ExpenseReimbursementAuditService",
    "CompensationAnalyticsService",
    "FMLALeaveAccrualService",
    "MultiStateTaxService",
    "TotalRewardsStatementService",
    "SuccessionPlanningService",
]
