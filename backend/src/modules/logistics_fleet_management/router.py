"""
Logistics & Fleet Management REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import FreightCarrier, ShipmentDispatch
from .schemas import (
    FreightCarrierCreate, FreightCarrierResponse,
    ShipmentDispatchCreate, TelematicsPingCreate
)
from .services import FreightRatingEngineService, TelematicsTrackingService

router = APIRouter(prefix="/logistics", tags=["Logistics & Fleet Management"])

@router.get("/carriers", response_model=List[FreightCarrierResponse])
async def list_carriers(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(FreightCarrier).where(
        FreightCarrier.tenant_id == user.tenant_id,
        FreightCarrier.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/carriers", response_model=FreightCarrierResponse, status_code=status.HTTP_201_CREATED)
async def create_carrier(
    payload: FreightCarrierCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    carrier = FreightCarrier(
        tenant_id=user.tenant_id,
        carrier_code=payload.carrier_code,
        company_name=payload.company_name,
        scac_code=payload.scac_code,
        dot_number=payload.dot_number,
        transport_mode=payload.transport_mode,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        is_preferred=payload.is_preferred
    )
    db.add(carrier)
    await db.commit()
    await db.refresh(carrier)
    return carrier

@router.post("/dispatches", status_code=status.HTTP_201_CREATED)
async def create_dispatch(
    payload: ShipmentDispatchCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await FreightRatingEngineService.create_rated_dispatch(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/telematics/ping")
async def record_telematics(
    payload: TelematicsPingCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await TelematicsTrackingService.record_telemetry(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id
    )
