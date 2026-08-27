"""
Field Service REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import ServiceTechnician, FieldWorkOrder
from .schemas import (
    ServiceTechnicianCreate, FieldWorkOrderCreate,
    DispatchAssignRequest, RecordPartUsageRequest
)
from .services import DispatchSchedulingService

router = APIRouter(prefix="/field-service", tags=["Field Service Operations"])

@router.get("/work-orders")
async def list_work_orders(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(FieldWorkOrder).where(
        FieldWorkOrder.tenant_id == user.tenant_id,
        FieldWorkOrder.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/work-orders", status_code=status.HTTP_201_CREATED)
async def create_work_order(
    payload: FieldWorkOrderCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await DispatchSchedulingService.create_work_order(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/dispatch")
async def dispatch_job(
    payload: DispatchAssignRequest,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await DispatchSchedulingService.dispatch_technician(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
