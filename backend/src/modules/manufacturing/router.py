"""
NexERP Manufacturing, BOM & MRP-II REST API Endpoints.
"""

from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.manufacturing.models import (
    WorkCenter,
    BillOfMaterials,
    ProductionOrder,
    JobCard,
    MRPSnapshot
)
from backend.src.modules.manufacturing.schemas import (
    WorkCenterCreate,
    WorkCenterResponse,
    BOMCreate,
    BOMResponse,
    ProductionOrderCreate,
    ProductionOrderResponse,
    JobCardTimeLogCreate,
    JobCardResponse,
    MRPRunRequest,
    MRPSnapshotResponse
)
from backend.src.modules.manufacturing.services import (
    WorkCenterService,
    BOMService,
    ProductionOrderService,
    MRPEngineService,
    ShopFloorService
)
from .execution_schemas import (DowntimeCreate, OperatorSessionCreate, OperatorSessionResponse,
                                QualityCheckCreate, QualityCheckResponse, ScrapCreate, ScrapDecision,
                                ScrapResponse)
from .execution_services import ManufacturingExecutionService

router = APIRouter(prefix="/manufacturing", tags=["Manufacturing, BOM & MRP-II"])


# ==============================================================================
# Work Centers
# ==============================================================================

@router.get("/work-centers", response_model=List[WorkCenterResponse])
async def list_work_centers(
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:work_centers:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List manufacturing work centers."""
    return await WorkCenterService.list_work_centers(db, current_user.tenant_id)


@router.post("/work-centers", response_model=WorkCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_work_center(
    payload: WorkCenterCreate,
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:work_centers:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a work center."""
    return await WorkCenterService.create_work_center(db, current_user.tenant_id, payload)


# ==============================================================================
# Bill of Materials (BOM)
# ==============================================================================

@router.get("/boms", response_model=List[BOMResponse])
async def list_boms(
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:bom:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List Bills of Materials."""
    return await BOMService.list_boms(db, current_user.tenant_id)


@router.post("/boms", response_model=BOMResponse, status_code=status.HTTP_201_CREATED)
async def create_bom(
    payload: BOMCreate,
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:bom:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a multi-level BOM."""
    return await BOMService.create_bom(db, current_user.tenant_id, payload)


@router.get("/boms/{item_id}/explode")
async def explode_bom(
    item_id: str,
    quantity: Decimal = Query(default=Decimal("1.0")),
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:bom:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Recursively explode multi-level BOM structure."""
    return await BOMService.explode_bom_multi_level(db, current_user.tenant_id, item_id, quantity)


# ==============================================================================
# Production / Work Orders
# ==============================================================================

@router.get("/orders", response_model=List[ProductionOrderResponse])
async def list_production_orders(
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List shop-floor Work Orders."""
    return await ProductionOrderService.list_orders(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/orders", response_model=ProductionOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_production_order(
    payload: ProductionOrderCreate,
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a Work Order with component material reservations."""
    return await ProductionOrderService.create_production_order(db, current_user.tenant_id, payload, current_user.id)


@router.post("/orders/{order_id}/complete", response_model=ProductionOrderResponse)
async def complete_production_order(
    order_id: str,
    completed_quantity: Decimal = Query(..., gt=0),
    location_id: str = Query(...),
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Complete production order, backflush materials from warehouse, and intake finished goods."""
    return await ProductionOrderService.complete_production_order(
        db, current_user.tenant_id, order_id, completed_quantity, location_id, current_user.id
    )


# ==============================================================================
# MRP-II Planning Runs
# ==============================================================================

@router.post("/mrp/run", response_model=MRPSnapshotResponse)
async def execute_mrp_run(
    payload: MRPRunRequest,
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:mrp:run")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute MRP calculation engine generating planned purchase and production orders."""
    return await MRPEngineService.run_mrp_calculation(
        db, current_user.tenant_id, payload.planning_horizon_days, current_user.id
    )


@router.get("/mrp/snapshots", response_model=List[MRPSnapshotResponse])
async def list_mrp_snapshots(
    current_user: CurrentUser = Depends(RequirePermission("manufacturing:mrp:run")),
    db: AsyncSession = Depends(get_db_session)
):
    """List historical MRP runs and planned orders."""
    return await MRPEngineService.list_snapshots(db, current_user.tenant_id)


@router.post("/execution/sessions", response_model=OperatorSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_operator_session(payload: OperatorSessionCreate, current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    return await ManufacturingExecutionService.create_session(db, current_user.tenant_id, payload)


@router.post("/execution/sessions/{session_id}/complete", response_model=OperatorSessionResponse)
async def complete_operator_session(session_id: str, hourly_rate: Decimal = Query(..., ge=0), current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    return await ManufacturingExecutionService.complete_session(db, current_user.tenant_id, session_id, hourly_rate)


@router.post("/execution/quality-checks", response_model=QualityCheckResponse, status_code=status.HTTP_201_CREATED)
async def create_quality_check(payload: QualityCheckCreate, current_user: CurrentUser = Depends(RequirePermission("quality:inspections:manage")), db: AsyncSession = Depends(get_db_session)):
    return await ManufacturingExecutionService.create_quality_check(db, current_user.tenant_id, payload, current_user.id)


@router.post("/execution/downtime", status_code=status.HTTP_201_CREATED)
async def create_downtime(payload: DowntimeCreate, current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    event = await ManufacturingExecutionService.create_downtime(db, current_user.tenant_id, payload, current_user.id)
    return event.to_dict()


@router.post("/execution/downtime/{event_id}/close")
async def close_downtime(event_id: str, current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    return (await ManufacturingExecutionService.close_downtime(db, current_user.tenant_id, event_id)).to_dict()


@router.post("/execution/scrap", response_model=ScrapResponse, status_code=status.HTTP_201_CREATED)
async def request_scrap(payload: ScrapCreate, current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    return await ManufacturingExecutionService.request_scrap(db, current_user.tenant_id, payload, current_user.id)


@router.post("/execution/scrap/{scrap_id}/decision", response_model=ScrapResponse)
async def decide_scrap(scrap_id: str, payload: ScrapDecision, current_user: CurrentUser = Depends(RequirePermission("manufacturing:orders:manage")), db: AsyncSession = Depends(get_db_session)):
    return await ManufacturingExecutionService.decide_scrap(db, current_user.tenant_id, scrap_id, payload, current_user.id)
