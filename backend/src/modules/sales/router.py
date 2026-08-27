"""
NexERP Sales & Customer Relationship Management (CRM) REST API Endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.sales.models import Lead, SalesQuotation, SalesOrder, FulfillmentDelivery
from backend.src.modules.sales.schemas import (
    LeadCreate,
    LeadResponse,
    SalesQuotationCreate,
    SalesQuotationResponse,
    SalesOrderCreate,
    SalesOrderResponse,
    FulfillmentDeliveryCreate,
    FulfillmentDeliveryResponse
)
from backend.src.modules.sales.services import (
    LeadService,
    QuotationService,
    SalesOrderService,
    FulfillmentService
)
from .crm_schemas import ActivityCreate, ActivityResponse, ForecastResponse, OpportunityCreate, OpportunityResponse, OpportunityUpdate
from .crm_services import CRMService

router = APIRouter(prefix="/sales", tags=["Sales CRM & Order Management"])


# ==============================================================================
# CRM Leads & Pipeline
# ==============================================================================

@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List CRM sales opportunities."""
    return await LeadService.list_leads(db, current_user.tenant_id)


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: LeadCreate,
    current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new sales lead."""
    return await LeadService.create_lead(db, current_user.tenant_id, payload)


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(payload: OpportunityCreate, current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.create_opportunity(db, current_user.tenant_id, payload)


@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(stage_code: Optional[str] = None, owner_id: Optional[str] = None, current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.list_opportunities(db, current_user.tenant_id, stage_code, owner_id)


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(opportunity_id: str, payload: OpportunityUpdate, current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.update_opportunity(db, current_user.tenant_id, opportunity_id, payload)


@router.post("/opportunities/forecast", response_model=ForecastResponse)
async def create_forecast(period_start: date, period_end: date, owner_id: Optional[str] = None, current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.forecast(db, current_user.tenant_id, period_start, period_end, owner_id)


@router.get("/opportunities/stage-summary")
async def opportunity_stage_summary(current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.stage_summary(db, current_user.tenant_id)


@router.post("/crm/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_crm_activity(payload: ActivityCreate, current_user: CurrentUser = Depends(RequirePermission("sales:leads:manage")), db: AsyncSession = Depends(get_db_session)):
    return await CRMService.add_activity(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Sales Quotations
# ==============================================================================

@router.get("/quotations", response_model=List[SalesQuotationResponse])
async def list_quotations(
    current_user: CurrentUser = Depends(RequirePermission("sales:quotes:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List commercial sales quotations."""
    query = (
        select(SalesQuotation)
        .where(SalesQuotation.tenant_id == current_user.tenant_id, SalesQuotation.is_deleted == False)
        .options(selectinload(SalesQuotation.lines))
        .order_by(SalesQuotation.quote_date.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/quotations", response_model=SalesQuotationResponse, status_code=status.HTTP_201_CREATED)
async def create_quotation(
    payload: SalesQuotationCreate,
    current_user: CurrentUser = Depends(RequirePermission("sales:quotes:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a sales quotation."""
    return await QuotationService.create_quotation(db, current_user.tenant_id, payload)


# ==============================================================================
# Sales Orders (SO)
# ==============================================================================

@router.get("/orders", response_model=List[SalesOrderResponse])
async def list_sales_orders(
    skip: int = 0,
    limit: int = 50,
    current_user: CurrentUser = Depends(RequirePermission("sales:orders:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """List customer Sales Orders."""
    return await SalesOrderService.list_sales_orders(db, current_user.tenant_id, skip=skip, limit=limit)


@router.post("/orders", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_sales_order(
    payload: SalesOrderCreate,
    current_user: CurrentUser = Depends(RequirePermission("sales:orders:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create and confirm Sales Order, reserve stock, and check credit limit."""
    return await SalesOrderService.create_sales_order(db, current_user.tenant_id, payload, current_user.id)


# ==============================================================================
# Fulfillment & Delivery
# ==============================================================================

@router.get("/deliveries", response_model=List[FulfillmentDeliveryResponse])
async def list_deliveries(
    current_user: CurrentUser = Depends(RequirePermission("sales:fulfillment:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List warehouse dispatch shipments."""
    query = (
        select(FulfillmentDelivery)
        .where(FulfillmentDelivery.tenant_id == current_user.tenant_id, FulfillmentDelivery.is_deleted == False)
        .options(selectinload(FulfillmentDelivery.lines))
        .order_by(FulfillmentDelivery.dispatch_date.desc())
    )
    res = await db.execute(query)
    return list(res.scalars().all())


@router.post("/deliveries", response_model=FulfillmentDeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(
    payload: FulfillmentDeliveryCreate,
    current_user: CurrentUser = Depends(RequirePermission("sales:fulfillment:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Pick, pack, ship delivery dispatch order and trigger inventory stock deduction."""
    return await FulfillmentService.create_fulfillment_delivery(db, current_user.tenant_id, payload, current_user.id)
