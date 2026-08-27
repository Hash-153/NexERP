"""REST endpoints for close governance and financial control workflows."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.core.database import get_db_session
from backend.src.core.dependencies import CurrentUser, RequirePermission
from .models import ApprovalRequest, CashForecastLine, CloseChecklist, ReconciliationException
from .schemas import ApprovalDecision, ApprovalPolicyCreate, ApprovalPolicyResponse, ApprovalRequestCreate, ApprovalRequestResponse, CashForecastCreate, CashForecastResponse, ChecklistComplete, CloseChecklistCreate, CloseChecklistResponse, CloseReadinessResponse, ReconciliationExceptionCreate, ReconciliationExceptionResponse, ReconciliationResolution
from .services import FinancialControlService

router = APIRouter(prefix="/financial-controls", tags=["Financial Controls"])


def manage():
    return RequirePermission("financials:period:close")


def read():
    return RequirePermission("financials:journal:view")


@router.post("/close-checklists", response_model=CloseChecklistResponse, status_code=status.HTTP_201_CREATED)
async def add_checklist(payload: CloseChecklistCreate, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.add_checklist_item(db, current_user.tenant_id, payload)


@router.post("/close-checklists/{item_id}/complete", response_model=CloseChecklistResponse)
async def complete_checklist(item_id: str, payload: ChecklistComplete, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.complete_checklist_item(db, current_user.tenant_id, item_id, payload, current_user.id)


@router.get("/periods/{period_id}/readiness", response_model=CloseReadinessResponse)
async def close_readiness(period_id: str, current_user: CurrentUser = Depends(read()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.readiness(db, current_user.tenant_id, period_id)


@router.post("/periods/{period_id}/lock")
async def lock_period(period_id: str, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    period = await FinancialControlService.lock_period(db, current_user.tenant_id, period_id)
    return {"period_id": period.id, "is_locked": period.is_locked}


@router.post("/approval-policies", response_model=ApprovalPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_policy(payload: ApprovalPolicyCreate, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.create_policy(db, current_user.tenant_id, payload)


@router.post("/approval-requests", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_approval(payload: ApprovalRequestCreate, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.request_approval(db, current_user.tenant_id, payload, current_user.id)


@router.post("/approval-requests/{request_id}/decision", response_model=ApprovalRequestResponse)
async def decide_approval(request_id: str, payload: ApprovalDecision, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.decide_approval(db, current_user.tenant_id, request_id, payload, current_user.id)


@router.post("/cash-forecast", response_model=CashForecastResponse, status_code=status.HTTP_201_CREATED)
async def add_cash_forecast(payload: CashForecastCreate, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.add_cash_line(db, current_user.tenant_id, payload)


@router.get("/cash-forecast/summary")
async def cash_forecast_summary(current_user: CurrentUser = Depends(read()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.cash_summary(db, current_user.tenant_id)


@router.post("/reconciliation-exceptions", response_model=ReconciliationExceptionResponse, status_code=status.HTTP_201_CREATED)
async def create_reconciliation_exception(payload: ReconciliationExceptionCreate, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.create_reconciliation_exception(db, current_user.tenant_id, payload)


@router.post("/reconciliation-exceptions/{exception_id}/resolve", response_model=ReconciliationExceptionResponse)
async def resolve_reconciliation_exception(exception_id: str, payload: ReconciliationResolution, current_user: CurrentUser = Depends(manage()), db: AsyncSession = Depends(get_db_session)):
    return await FinancialControlService.resolve_reconciliation_exception(db, current_user.tenant_id, exception_id, payload, current_user.id)
