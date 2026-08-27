"""
Contract Lifecycle Management REST API Router.
"""
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import ContractDocument
from .schemas import ContractDocumentCreate, ContractDocumentResponse
from .services import ContractAuthoringService

router = APIRouter(prefix="/contracts", tags=["Contract Lifecycle Management"])

@router.get("/documents", response_model=List[ContractDocumentResponse])
async def list_contracts(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(ContractDocument).where(
        ContractDocument.tenant_id == user.tenant_id,
        ContractDocument.is_deleted == False
    )
    res = await db.execute(stmt)
    return res.scalars().all()

@router.post("/documents", response_model=ContractDocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractDocumentCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await ContractAuthoringService.create_contract(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
