"""
Customer Self-Service Portal REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import CustomerSupportTicket, CustomerRMARequest
from .schemas import SupportTicketCreate, RMARequestCreate
from .services import RMAReturnsService

router = APIRouter(prefix="/customer-portal", tags=["Customer Self-Service Portal"])

@router.get("/rmas")
async def list_rmas(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(CustomerRMARequest).where(
        CustomerRMARequest.tenant_id == user.tenant_id,
        CustomerRMARequest.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/rmas", status_code=status.HTTP_201_CREATED)
async def request_rma(
    payload: RMARequestCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await RMAReturnsService.create_rma(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
