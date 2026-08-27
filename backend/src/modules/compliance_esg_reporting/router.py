"""
ESG & Carbon Emissions REST API Router.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import FacilityEnergyEmissionLog
from .schemas import EmissionLogCreate, EmissionLogResponse, SupplierESGAuditCreate
from .services import GHGEmissionsCalculatorService

router = APIRouter(prefix="/esg", tags=["ESG Compliance & Carbon Accounting"])

@router.get("/emissions", response_model=List[EmissionLogResponse])
async def list_emission_logs(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(FacilityEnergyEmissionLog).where(
        FacilityEnergyEmissionLog.tenant_id == user.tenant_id,
        FacilityEnergyEmissionLog.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/emissions", response_model=EmissionLogResponse, status_code=status.HTTP_201_CREATED)
async def log_emissions(
    payload: EmissionLogCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await GHGEmissionsCalculatorService.log_emission_activity(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.get("/summary")
async def get_emissions_summary(
    period: str = Query("2026-Q1"),
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await GHGEmissionsCalculatorService.get_period_summary(
        session=db,
        period=period,
        tenant_id=user.tenant_id
    )
