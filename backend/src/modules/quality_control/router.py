"""
NexERP Quality Control (QA/QC) REST API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.quality_control.models import (
    QualityInspectionPlan,
    InspectionRecord,
    NonConformanceReport
)
from backend.src.modules.quality_control.schemas import (
    QualityPlanCreate,
    QualityPlanResponse,
    InspectionRecordCreate,
    InspectionRecordResponse,
    NCRCreate,
    NCRResponse
)
from backend.src.modules.quality_control.services import (
    QualityPlanService,
    InspectionService,
    NCRService
)

router = APIRouter(prefix="/quality", tags=["Quality Assurance & Control (QA/QC)"])


# ==============================================================================
# Quality Inspection Plans
# ==============================================================================

@router.get("/plans", response_model=List[QualityPlanResponse])
async def list_quality_plans(
    current_user: CurrentUser = Depends(RequirePermission("quality:plans:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List quality inspection plans and test criteria."""
    return await QualityPlanService.list_plans(db, current_user.tenant_id)


@router.post("/plans", response_model=QualityPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_quality_plan(
    payload: QualityPlanCreate,
    current_user: CurrentUser = Depends(RequirePermission("quality:plans:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a quality inspection plan."""
    return await QualityPlanService.create_plan(db, current_user.tenant_id, payload)


# ==============================================================================
# Inspection Records
# ==============================================================================

@router.get("/inspections", response_model=List[InspectionRecordResponse])
async def list_inspections(
    current_user: CurrentUser = Depends(RequirePermission("quality:inspections:execute")),
    db: AsyncSession = Depends(get_db_session)
):
    """List QA/QC inspection test records."""
    return await InspectionService.list_inspections(db, current_user.tenant_id)


@router.post("/inspections", response_model=InspectionRecordResponse, status_code=status.HTTP_201_CREATED)
async def execute_inspection(
    payload: InspectionRecordCreate,
    current_user: CurrentUser = Depends(RequirePermission("quality:inspections:execute")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute quality test inspection, evaluate tolerances, and determine lot conformance."""
    return await InspectionService.execute_inspection(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Non-Conformance Reports (NCR) & CAPA
# ==============================================================================

@router.get("/ncrs", response_model=List[NCRResponse])
async def list_ncrs(
    current_user: CurrentUser = Depends(RequirePermission("quality:ncr:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List Non-Conformance Reports and CAPA tickets."""
    return await NCRService.list_ncrs(db, current_user.tenant_id)


@router.post("/ncrs", response_model=NCRResponse, status_code=status.HTTP_201_CREATED)
async def file_ncr(
    payload: NCRCreate,
    current_user: CurrentUser = Depends(RequirePermission("quality:ncr:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """File a Non-Conformance Report."""
    return await NCRService.file_ncr(db, current_user.tenant_id, payload)


@router.post("/ncrs/{ncr_id}/close", response_model=NCRResponse)
async def close_ncr(
    ncr_id: str,
    current_user: CurrentUser = Depends(RequirePermission("quality:ncr:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Close and sign off on an NCR after corrective action verification."""
    return await NCRService.close_ncr(db, current_user.tenant_id, ncr_id)
