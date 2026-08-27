"""
Advanced Planning & Scheduling REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import ProductionWorkCenterResource, ScheduledManufacturingOperation
from .schemas import WorkCenterResourceCreate, ScheduledOperationInput
from .services import FiniteCapacitySchedulerService

router = APIRouter(prefix="/aps", tags=["Production Scheduling (APS)"])

@router.get("/work-centers")
async def list_work_centers(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(ProductionWorkCenterResource).where(
        ProductionWorkCenterResource.tenant_id == user.tenant_id,
        ProductionWorkCenterResource.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/work-centers", status_code=status.HTTP_201_CREATED)
async def create_work_center(
    payload: WorkCenterResourceCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    wc = ProductionWorkCenterResource(
        tenant_id=user.tenant_id,
        code=payload.code,
        name=payload.name,
        plant_facility_id=payload.plant_facility_id,
        department=payload.department,
        daily_shift_hours=payload.daily_shift_hours,
        number_of_machines=payload.number_of_machines,
        hourly_standard_cost=payload.hourly_standard_cost,
        is_bottleneck_critical=payload.is_bottleneck_critical
    )
    db.add(wc)
    await db.commit()
    await db.refresh(wc)
    return wc

@router.post("/schedule", status_code=status.HTTP_201_CREATED)
async def schedule_production_job(
    payload: ScheduledOperationInput,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await FiniteCapacitySchedulerService.schedule_operation(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
