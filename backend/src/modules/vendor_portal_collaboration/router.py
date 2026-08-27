"""
Vendor Collaboration Portal REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import AdvanceShippingNoticeASN
from .schemas import ASNSubmissionCreate
from .services import ASNDispatchService

router = APIRouter(prefix="/vendor-portal", tags=["Vendor Collaboration Portal"])

@router.get("/asns")
async def list_asns(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(AdvanceShippingNoticeASN).where(
        AdvanceShippingNoticeASN.tenant_id == user.tenant_id,
        AdvanceShippingNoticeASN.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/asns", status_code=status.HTTP_201_CREATED)
async def submit_asn(
    payload: ASNSubmissionCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await ASNDispatchService.submit_asn(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
