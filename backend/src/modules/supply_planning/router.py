"""Supply planning REST endpoints."""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.core.database import get_db_session
from backend.src.core.dependencies import CurrentUser, RequirePermission
from .schemas import ForecastCreate, ForecastResponse, MilestoneCreate, MilestoneResponse, PolicyCreate, PolicyResponse, RecommendationResponse, ScorecardCreate, ScorecardResponse
from .services import SupplyPlanningService

router = APIRouter(prefix="/supply-planning", tags=["Supply Planning"])


@router.post("/forecasts", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
async def create_forecast(payload: ForecastCreate, current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.create_forecast(db, current_user.tenant_id, payload)


@router.post("/policies", response_model=PolicyResponse)
async def save_policy(payload: PolicyCreate, current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.upsert_policy(db, current_user.tenant_id, payload)


@router.post("/recommendations", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def create_recommendation(item_id: str, warehouse_id: str, available_quantity: Decimal, demand_quantity: Decimal, required_date: date, estimated_unit_cost: Decimal = Decimal("0"), current_user: CurrentUser = Depends(RequirePermission("inventory:items:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.recommend(db, current_user.tenant_id, item_id, warehouse_id, available_quantity, demand_quantity, required_date, estimated_unit_cost)


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def list_recommendations(recommendation_status: Optional[str] = None, current_user: CurrentUser = Depends(RequirePermission("inventory:items:view")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.list_recommendations(db, current_user.tenant_id, recommendation_status)


@router.post("/supplier-scorecards", response_model=ScorecardResponse, status_code=status.HTTP_201_CREATED)
async def create_scorecard(payload: ScorecardCreate, current_user: CurrentUser = Depends(RequirePermission("procurement:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.create_scorecard(db, current_user.tenant_id, payload)


@router.post("/shipments/milestones", response_model=MilestoneResponse, status_code=status.HTTP_201_CREATED)
async def create_milestone(payload: MilestoneCreate, current_user: CurrentUser = Depends(RequirePermission("procurement:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.create_milestone(db, current_user.tenant_id, payload)


@router.post("/shipments/milestones/{milestone_id}/complete", response_model=MilestoneResponse)
async def complete_milestone(milestone_id: str, delay_reason: Optional[str] = None, current_user: CurrentUser = Depends(RequirePermission("procurement:manage")), db: AsyncSession = Depends(get_db_session)):
    return await SupplyPlanningService.complete_milestone(db, current_user.tenant_id, milestone_id, delay_reason)
