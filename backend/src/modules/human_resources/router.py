"""
NexERP Human Resources & Payroll REST API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.human_resources.models import (
    Department,
    JobPosition,
    Employee,
    LeaveType,
    LeaveRequest,
    AttendanceLog,
    PayrollRun,
    ExpenseClaim
)
from backend.src.modules.human_resources.schemas import (
    DepartmentCreate,
    DepartmentResponse,
    JobPositionCreate,
    JobPositionResponse,
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    LeaveTypeCreate,
    LeaveTypeResponse,
    LeaveRequestCreate,
    LeaveRequestResponse,
    AttendanceLogCreate,
    AttendanceLogResponse,
    PayrollRunCreate,
    PayrollRunResponse,
    ExpenseClaimCreate,
    ExpenseClaimResponse
)
from backend.src.modules.human_resources.services import (
    EmployeeService,
    AttendanceService,
    LeaveService,
    PayrollCalculationService,
    ExpenseClaimService
)

router = APIRouter(prefix="/hr", tags=["Human Resources & Payroll"])


# ==============================================================================
# Departments & Job Positions
# ==============================================================================

@router.get("/departments", response_model=List[DepartmentResponse])
async def list_departments(
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List organizational departments."""
    return await EmployeeService.list_departments(db, current_user.tenant_id)


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new department."""
    return await EmployeeService.create_department(db, current_user.tenant_id, payload)


@router.get("/job-positions", response_model=List[JobPositionResponse])
async def list_job_positions(
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List job roles."""
    return await EmployeeService.list_job_positions(db, current_user.tenant_id)


@router.post("/job-positions", response_model=JobPositionResponse, status_code=status.HTTP_201_CREATED)
async def create_job_position(
    payload: JobPositionCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a job position."""
    return await EmployeeService.create_job_position(db, current_user.tenant_id, payload)


# ==============================================================================
# Employee Directory
# ==============================================================================

@router.get("/employees", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List employee master records."""
    return await EmployeeService.list_employees(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/employees", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    payload: EmployeeCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create an employee profile."""
    return await EmployeeService.create_employee(db, current_user.tenant_id, payload)


# ==============================================================================
# Attendance & Leaves
# ==============================================================================

@router.post("/attendance", response_model=AttendanceLogResponse, status_code=status.HTTP_201_CREATED)
async def log_attendance(
    payload: AttendanceLogCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:attendance:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Record employee attendance punch."""
    return await AttendanceService.log_attendance(db, current_user.tenant_id, payload)


@router.get("/attendance", response_model=List[AttendanceLogResponse])
async def list_attendance(
    employee_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("hr:attendance:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List attendance punches."""
    return await AttendanceService.list_attendance(db, current_user.tenant_id, employee_id)


@router.post("/leaves/apply", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
async def apply_leave(
    payload: LeaveRequestCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:leaves:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit a leave application."""
    return await LeaveService.submit_leave_request(db, current_user.tenant_id, payload)


@router.post("/leaves/{request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave(
    request_id: str,
    current_user: CurrentUser = Depends(RequirePermission("hr:leaves:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Approve a leave application."""
    return await LeaveService.approve_leave_request(db, current_user.tenant_id, request_id, current_user.id)


@router.get("/leaves", response_model=List[LeaveRequestResponse])
async def list_leaves(
    employee_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("hr:leaves:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List employee leave requests."""
    return await LeaveService.list_leave_requests(db, current_user.tenant_id, employee_id)


# ==============================================================================
# Payroll Calculation & Payslips
# ==============================================================================

@router.get("/payroll/runs", response_model=List[PayrollRunResponse])
async def list_payroll_runs(
    current_user: CurrentUser = Depends(RequirePermission("hr:payroll:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List monthly payroll runs and payslips."""
    return await PayrollCalculationService.list_payroll_runs(db, current_user.tenant_id)


@router.post("/payroll/execute", response_model=PayrollRunResponse, status_code=status.HTTP_201_CREATED)
async def execute_payroll(
    payload: PayrollRunCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:payroll:execute")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute monthly progressive tax bracket payroll batch and post GL salaries accrual."""
    return await PayrollCalculationService.execute_payroll_run(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Expense Claims
# ==============================================================================

@router.get("/expenses", response_model=List[ExpenseClaimResponse])
async def list_expense_claims(
    employee_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List employee expense reimbursement claims."""
    return await ExpenseClaimService.list_expense_claims(db, current_user.tenant_id, employee_id)


@router.post("/expenses", response_model=ExpenseClaimResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_claim(
    payload: ExpenseClaimCreate,
    current_user: CurrentUser = Depends(RequirePermission("hr:employees:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit an expense reimbursement claim."""
    return await ExpenseClaimService.create_expense_claim(db, current_user.tenant_id, payload)
