"""
NexERP Accounts Receivable (AR) REST API Endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.accounts_receivable.models import Customer, SalesInvoice, PaymentReceipt
from backend.src.modules.accounts_receivable.schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    SalesInvoiceCreate,
    SalesInvoiceResponse,
    PaymentReceiptCreate,
    PaymentReceiptResponse,
    ARAgingReportResponse
)
from backend.src.modules.accounts_receivable.services import (
    CustomerService,
    SalesInvoiceService,
    PaymentReceiptService,
    DunningService,
    ARAgingService
)

router = APIRouter(prefix="/accounts-receivable", tags=["Accounts Receivable & Customer Invoicing"])


# ==============================================================================
# Customer Master Directory
# ==============================================================================

@router.get("/customers", response_model=List[CustomerResponse])
async def list_customers(
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser = Depends(RequirePermission("ar:customers:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List customer accounts and credit status."""
    return await CustomerService.list_customers(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    current_user: CurrentUser = Depends(RequirePermission("ar:customers:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new customer profile."""
    return await CustomerService.create_customer(db, current_user.tenant_id, payload)


# ==============================================================================
# Sales Invoices
# ==============================================================================

@router.get("/invoices", response_model=List[SalesInvoiceResponse])
async def list_sales_invoices(
    skip: int = 0,
    limit: int = 50,
    customer_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("ar:invoices:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List sales invoices with optional customer and status filters."""
    query = (
        select(SalesInvoice)
        .where(SalesInvoice.tenant_id == current_user.tenant_id, SalesInvoice.is_deleted == False)
        .options(selectinload(SalesInvoice.lines))
        .order_by(SalesInvoice.invoice_date.desc(), SalesInvoice.invoice_number.desc())
        .offset(skip)
        .limit(limit)
    )
    if customer_id:
        query = query.where(SalesInvoice.customer_id == customer_id)
    if status_filter:
        query = query.where(SalesInvoice.status == status_filter.upper())

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/invoices", response_model=SalesInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_invoice(
    payload: SalesInvoiceCreate,
    current_user: CurrentUser = Depends(RequirePermission("ar:invoices:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new draft sales invoice."""
    return await SalesInvoiceService.create_invoice(db, current_user.tenant_id, payload, current_user.id)


@router.post("/invoices/{invoice_id}/post", response_model=SalesInvoiceResponse)
async def post_sales_invoice(
    invoice_id: str,
    current_user: CurrentUser = Depends(RequirePermission("ar:invoices:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Post sales invoice to General Ledger (Debit AR, Credit Revenue/Taxes)."""
    return await SalesInvoiceService.post_sales_invoice(db, current_user.tenant_id, invoice_id, current_user.id)


# ==============================================================================
# Payment Receipts & Allocations
# ==============================================================================

@router.get("/receipts", response_model=List[PaymentReceiptResponse])
async def list_payment_receipts(
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(RequirePermission("ar:receipts:record")),
    db: AsyncSession = Depends(get_db_session)
):
    """List customer payment receipts."""
    query = (
        select(PaymentReceipt)
        .where(PaymentReceipt.tenant_id == current_user.tenant_id, PaymentReceipt.is_deleted == False)
        .options(selectinload(PaymentReceipt.allocations))
        .order_by(PaymentReceipt.receipt_date.desc(), PaymentReceipt.receipt_number.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/receipts", response_model=PaymentReceiptResponse, status_code=status.HTTP_201_CREATED)
async def record_payment_receipt(
    payload: PaymentReceiptCreate,
    current_user: CurrentUser = Depends(RequirePermission("ar:receipts:record")),
    db: AsyncSession = Depends(get_db_session)
):
    """Record customer payment receipt, allocate to open invoices, and post bank entry."""
    return await PaymentReceiptService.record_payment_receipt(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# AR Aging Report & Dunning
# ==============================================================================

@router.get("/reports/aging", response_model=ARAgingReportResponse)
async def get_ar_aging_report(
    as_of_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("ar:invoices:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate Accounts Receivable aging breakdown and DSO analysis."""
    return await ARAgingService.generate_aging_report(db, current_user.tenant_id, as_of_date)


@router.post("/dunning/run")
async def trigger_dunning_run(
    as_of_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("ar:dunning:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Process dunning cycle, advancing delinquent stages and calculating interest charges."""
    notices = await DunningService.process_dunning_cycle(db, current_user.tenant_id, as_of_date)
    return {"message": f"Dunning cycle executed. Generated {len(notices)} notices.", "notices_count": len(notices)}
