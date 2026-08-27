"""
NexERP Accounts Payable (AP) REST API Endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.accounts_payable.models import Vendor, VendorBill, PaymentRun
from backend.src.modules.accounts_payable.schemas import (
    VendorCreate,
    VendorUpdate,
    VendorResponse,
    VendorBillCreate,
    VendorBillResponse,
    ThreeWayMatchResponse,
    PaymentRunCreate,
    PaymentRunResponse,
    APAgingReportResponse
)
from backend.src.modules.accounts_payable.services import (
    VendorService,
    VendorBillService,
    ThreeWayMatchService,
    PaymentRunService,
    APAgingService
)

router = APIRouter(prefix="/accounts-payable", tags=["Accounts Payable & Vendor Billing"])


# ==============================================================================
# Vendor Master Directory
# ==============================================================================

@router.get("/vendors", response_model=List[VendorResponse])
async def list_vendors(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(RequirePermission("ap:vendors:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all registered suppliers and vendors."""
    return await VendorService.list_vendors(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/vendors", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    payload: VendorCreate,
    current_user: CurrentUser = Depends(RequirePermission("ap:vendors:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new vendor profile."""
    return await VendorService.create_vendor(db, current_user.tenant_id, payload)


# ==============================================================================
# Vendor Bills & Invoices
# ==============================================================================

@router.get("/bills", response_model=List[VendorBillResponse])
async def list_vendor_bills(
    skip: int = 0,
    limit: int = 50,
    vendor_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("ap:bills:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List vendor bills with optional filtering by vendor and payment status."""
    query = (
        select(VendorBill)
        .where(VendorBill.tenant_id == current_user.tenant_id, VendorBill.is_deleted == False)
        .options(selectinload(VendorBill.lines))
        .order_by(VendorBill.bill_date.desc(), VendorBill.system_reference.desc())
        .offset(skip)
        .limit(limit)
    )
    if vendor_id:
        query = query.where(VendorBill.vendor_id == vendor_id)
    if status_filter:
        query = query.where(VendorBill.status == status_filter.upper())

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/bills", response_model=VendorBillResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor_bill(
    payload: VendorBillCreate,
    current_user: CurrentUser = Depends(RequirePermission("ap:bills:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Record a new vendor bill."""
    return await VendorBillService.create_bill(db, current_user.tenant_id, payload, current_user.id)


@router.post("/bills/{bill_id}/approve", response_model=VendorBillResponse)
async def approve_vendor_bill(
    bill_id: str,
    current_user: CurrentUser = Depends(RequirePermission("ap:bills:approve")),
    db: AsyncSession = Depends(get_db_session)
):
    """Approve bill and automatically post double-entry General Ledger accrual voucher."""
    return await VendorBillService.approve_and_post_bill(db, current_user.tenant_id, bill_id, current_user.id)


@router.post("/bills/{bill_id}/three-way-match", response_model=ThreeWayMatchResponse)
async def verify_three_way_match(
    bill_id: str,
    po_id: Optional[str] = None,
    grn_id: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("ap:bills:approve")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute 3-way matching tolerance validation for the bill."""
    return await ThreeWayMatchService.verify_bill_match(db, current_user.tenant_id, bill_id, po_id, grn_id)


# ==============================================================================
# Payment Runs & Disbursements
# ==============================================================================

@router.get("/payment-runs", response_model=List[PaymentRunResponse])
async def list_payment_runs(
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(RequirePermission("ap:payments:process")),
    db: AsyncSession = Depends(get_db_session)
):
    """List batch payment runs."""
    query = (
        select(PaymentRun)
        .where(PaymentRun.tenant_id == current_user.tenant_id, PaymentRun.is_deleted == False)
        .options(selectinload(PaymentRun.items))
        .order_by(PaymentRun.run_date.desc(), PaymentRun.run_number.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/payment-runs", response_model=PaymentRunResponse, status_code=status.HTTP_201_CREATED)
async def execute_payment_run(
    payload: PaymentRunCreate,
    current_user: CurrentUser = Depends(RequirePermission("ap:payments:process")),
    db: AsyncSession = Depends(get_db_session)
):
    """Execute batch payment disbursement, updating bill balances and posting GL cash entry."""
    return await PaymentRunService.execute_payment_run(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# AP Aging Report
# ==============================================================================

@router.get("/reports/aging", response_model=APAgingReportResponse)
async def get_ap_aging_report(
    as_of_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("ap:bills:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate Accounts Payable aging matrix report."""
    return await APAgingService.generate_aging_report(db, current_user.tenant_id, as_of_date)
