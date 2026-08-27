"""
NexERP Vendor Directory & Master Management Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.accounts_payable.models import Vendor
from backend.src.modules.accounts_payable.schemas import VendorCreate, VendorUpdate


class VendorService:
    """
    Vendor supplier directory service.
    """

    @classmethod
    async def create_vendor(cls, db: AsyncSession, tenant_id: str, payload: VendorCreate) -> Vendor:
        query = select(Vendor).where(
            Vendor.tenant_id == tenant_id,
            Vendor.code == payload.code.strip(),
            Vendor.is_deleted == False
        )
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Vendor with code '{payload.code}' already exists.")

        vendor = Vendor(
            tenant_id=tenant_id,
            code=payload.code.strip(),
            name=payload.name.strip(),
            tax_identifier=payload.tax_identifier,
            payment_terms_days=payload.payment_terms_days,
            credit_limit=payload.credit_limit,
            currency=payload.currency.upper(),
            email=payload.email,
            phone=payload.phone,
            address=payload.address,
            bank_account_details=payload.bank_account_details,
            ap_account_id=payload.ap_account_id,
            expense_account_id=payload.expense_account_id,
            is_1099_eligible=payload.is_1099_eligible
        )
        db.add(vendor)
        await db.commit()
        await db.refresh(vendor)
        return vendor

    @classmethod
    async def get_vendor(cls, db: AsyncSession, tenant_id: str, vendor_id: str) -> Optional[Vendor]:
        query = select(Vendor).where(
            Vendor.id == vendor_id,
            Vendor.tenant_id == tenant_id,
            Vendor.is_deleted == False
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def list_vendors(cls, db: AsyncSession, tenant_id: str, skip: int = 0, limit: int = 100) -> List[Vendor]:
        query = (
            select(Vendor)
            .where(Vendor.tenant_id == tenant_id, Vendor.is_deleted == False)
            .order_by(Vendor.name.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())
