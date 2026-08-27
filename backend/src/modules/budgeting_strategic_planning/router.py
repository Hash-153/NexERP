"""
Strategic Budgeting REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import StrategicBudgetPlan
from .schemas import StrategicBudgetPlanCreate, StrategicBudgetPlanResponse
from .services import BudgetPlanningService

router = APIRouter(prefix="/budgeting", tags=["Budgeting & Strategic Planning"])

@router.get("/plans", response_model=List[StrategicBudgetPlanResponse])
async def list_budget_plans(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(StrategicBudgetPlan).where(
        StrategicBudgetPlan.tenant_id == user.tenant_id,
        StrategicBudgetPlan.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/plans", response_model=StrategicBudgetPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_budget_plan(
    payload: StrategicBudgetPlanCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await BudgetPlanningService.create_annual_plan(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
