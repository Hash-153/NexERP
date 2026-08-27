"""
Advanced WMS REST API Router.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import WarehouseZone, WarehouseLocation, WaveBatchRun
from .schemas import (
    WarehouseZoneCreate, WarehouseZoneResponse,
    WarehouseLocationCreate, WarehouseLocationResponse,
    WaveBatchCreate, WaveBatchResponse, PickExecutionRequest
)
from .services import SlottingOptimizationService, WavePickingOrchestratorService, YardDockService

router = APIRouter(prefix="/wms", tags=["Advanced Warehouse Management (WMS)"])

@router.get("/zones", response_model=List[WarehouseZoneResponse])
async def list_zones(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(WarehouseZone).where(
        WarehouseZone.tenant_id == user.tenant_id,
        WarehouseZone.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/zones", response_model=WarehouseZoneResponse, status_code=status.HTTP_201_CREATED)
async def create_zone(
    payload: WarehouseZoneCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    zone = WarehouseZone(
        tenant_id=user.tenant_id,
        warehouse_id=payload.warehouse_id,
        zone_code=payload.zone_code,
        name=payload.name,
        zone_type=payload.zone_type,
        temperature_min_c=payload.temperature_min_c,
        temperature_max_c=payload.temperature_max_c,
        is_bonded=payload.is_bonded,
        is_hazardous=payload.is_hazardous
    )
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone

@router.post("/slotting/optimize")
async def optimize_slotting(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await SlottingOptimizationService.analyze_and_reclassify_slotting(
        session=db,
        tenant_id=user.tenant_id
    )

@router.post("/waves", response_model=WaveBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_wave(
    payload: WaveBatchCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await WavePickingOrchestratorService.release_wave(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/pick/confirm")
async def confirm_pick_task(
    payload: PickExecutionRequest,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    task = await WavePickingOrchestratorService.record_pick_completion(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
    return {"status": "SUCCESS", "task_id": task.id, "picked_qty": float(task.picked_qty)}
