"""
CRM & CPQ REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import CRMLead, CRMOpportunity, CPQQuote
from .schemas import CRMLeadCreate, CRMLeadResponse, CRMOpportunityCreate, CPQQuoteCreate
from .services import LeadScoringEngineService, CPQPricingEngineService

router = APIRouter(prefix="/crm", tags=["CRM & Opportunity Pipeline"])

@router.get("/leads", response_model=List[CRMLeadResponse])
async def list_leads(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(CRMLead).where(
        CRMLead.tenant_id == user.tenant_id,
        CRMLead.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/leads", response_model=CRMLeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: CRMLeadCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await LeadScoringEngineService.create_and_score_lead(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/quotes", status_code=status.HTTP_201_CREATED)
async def generate_cpq_quote(
    payload: CPQQuoteCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    quote = await CPQPricingEngineService.generate_quote(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
    return {
        "status": "CREATED",
        "quote_id": quote.id,
        "quote_number": quote.quote_number,
        "net_total": float(quote.net_total),
        "margin_percentage": float(quote.margin_percentage)
    }
