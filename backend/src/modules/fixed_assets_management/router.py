"""
Fixed Assets Management REST API Router.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import FixedAssetMaster
from .schemas import FixedAssetMasterCreate, FixedAssetMasterResponse, DepreciationRunRequest, PhysicalAuditScan
from .services import DepreciationEngineService, AssetLifecycleService

router = APIRouter(prefix="/fixed-assets", tags=["Fixed Assets Management"])

@router.get("/assets", response_model=List[FixedAssetMasterResponse])
async def list_fixed_assets(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(FixedAssetMaster).where(
        FixedAssetMaster.tenant_id == user.tenant_id,
        FixedAssetMaster.is_deleted == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/assets", response_model=FixedAssetMasterResponse, status_code=status.HTTP_201_CREATED)
async def create_fixed_asset(
    payload: FixedAssetMasterCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await AssetLifecycleService.create_asset(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/depreciation/run")
async def execute_depreciation(
    payload: DepreciationRunRequest,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await DepreciationEngineService.run_monthly_depreciation(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/audits/scan")
async def record_audit_scan(
    payload: PhysicalAuditScan,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await AssetLifecycleService.record_physical_audit(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
