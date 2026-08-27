"""
NexERP Procurement & Supply Chain (SCM) REST API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.procurement.models import (
    PurchaseRequisition,
    PurchaseOrder,
    GoodsReceiptNote,
    VendorEvaluation
)
from backend.src.modules.procurement.schemas import (
    RequisitionCreate,
    RequisitionResponse,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    GoodsReceiptNoteCreate,
    GoodsReceiptNoteResponse,
    VendorEvaluationCreate,
    VendorEvaluationResponse
)
from backend.src.modules.procurement.services import (
    RequisitionService,
    PurchaseOrderService,
    GoodsReceiptService,
    VendorEvaluationService
)

router = APIRouter(prefix="/procurement", tags=["Procurement & Supply Chain Management"])


# ==============================================================================
# Purchase Requisitions
# ==============================================================================

@router.get("/requisitions", response_model=List[RequisitionResponse])
async def list_requisitions(
    current_user: CurrentUser = Depends(RequirePermission("procurement:requisitions:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List purchase requisitions."""
    query = (
        select(PurchaseRequisition)
        .where(PurchaseRequisition.tenant_id == current_user.tenant_id, PurchaseRequisition.is_deleted == False)
        .options(selectinload(PurchaseRequisition.lines))
        .order_by(PurchaseRequisition.created_at.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/requisitions", response_model=RequisitionResponse, status_code=status.HTTP_201_CREATED)
async def create_requisition(
    payload: RequisitionCreate,
    current_user: CurrentUser = Depends(RequirePermission("procurement:requisitions:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Submit a purchase requisition."""
    return await RequisitionService.create_requisition(db, current_user.tenant_id, payload, current_user.id)


@router.post("/requisitions/{requisition_id}/approve", response_model=RequisitionResponse)
async def approve_requisition(
    requisition_id: str,
    current_user: CurrentUser = Depends(RequirePermission("procurement:requisitions:approve")),
    db: AsyncSession = Depends(get_db_session)
):
    """Approve spend requisition."""
    return await RequisitionService.approve_requisition(db, current_user.tenant_id, requisition_id, current_user.id)


# ==============================================================================
# Purchase Orders (PO)
# ==============================================================================

@router.get("/orders", response_model=List[PurchaseOrderResponse])
async def list_purchase_orders(
    skip: int = 0,
    limit: int = 50,
    vendor_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("procurement:orders:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List Purchase Orders."""
    query = (
        select(PurchaseOrder)
        .where(PurchaseOrder.tenant_id == current_user.tenant_id, PurchaseOrder.is_deleted == False)
        .options(selectinload(PurchaseOrder.lines))
        .order_by(PurchaseOrder.order_date.desc(), PurchaseOrder.po_number.desc())
        .offset(skip)
        .limit(limit)
    )
    if vendor_id:
        query = query.where(PurchaseOrder.vendor_id == vendor_id)

    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    current_user: CurrentUser = Depends(RequirePermission("procurement:orders:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new Purchase Order."""
    return await PurchaseOrderService.create_purchase_order(db, current_user.tenant_id, payload, current_user.id)


@router.post("/orders/{po_id}/approve", response_model=PurchaseOrderResponse)
async def approve_purchase_order(
    po_id: str,
    current_user: CurrentUser = Depends(RequirePermission("procurement:orders:approve")),
    db: AsyncSession = Depends(get_db_session)
):
    """Formally approve and issue Purchase Order."""
    return await PurchaseOrderService.approve_purchase_order(db, current_user.tenant_id, po_id, current_user.id)


# ==============================================================================
# Goods Receipt Notes (GRN)
# ==============================================================================

@router.get("/receipts", response_model=List[GoodsReceiptNoteResponse])
async def list_goods_receipts(
    current_user: CurrentUser = Depends(RequirePermission("procurement:receipts:record")),
    db: AsyncSession = Depends(get_db_session)
):
    """List Goods Receipt Notes."""
    query = (
        select(GoodsReceiptNote)
        .where(GoodsReceiptNote.tenant_id == current_user.tenant_id, GoodsReceiptNote.is_deleted == False)
        .options(selectinload(GoodsReceiptNote.lines))
        .order_by(GoodsReceiptNote.receipt_date.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/receipts", response_model=GoodsReceiptNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_goods_receipt(
    payload: GoodsReceiptNoteCreate,
    current_user: CurrentUser = Depends(RequirePermission("procurement:receipts:record")),
    db: AsyncSession = Depends(get_db_session)
):
    """Log receiving dock shipment arrival and update inventory stock."""
    return await GoodsReceiptService.create_goods_receipt(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Vendor Evaluations & Scorecards
# ==============================================================================

@router.get("/evaluations", response_model=List[VendorEvaluationResponse])
async def list_evaluations(
    vendor_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("procurement:orders:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List vendor performance scorecards."""
    return await VendorEvaluationService.list_evaluations(db, current_user.tenant_id, vendor_id)


@router.post("/evaluations", response_model=VendorEvaluationResponse, status_code=status.HTTP_201_CREATED)
async def evaluate_vendor(
    payload: VendorEvaluationCreate,
    current_user: CurrentUser = Depends(RequirePermission("procurement:orders:approve")),
    db: AsyncSession = Depends(get_db_session)
):
    """Record a vendor performance rating scorecard."""
    return await VendorEvaluationService.evaluate_vendor(db, current_user.tenant_id, payload, current_user.id)
