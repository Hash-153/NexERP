"""
NexERP Tenant Organization Provisioning Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.auth.models import Tenant
from backend.src.modules.auth.schemas import TenantCreate


class TenantService:
    """
    Manages creation, onboarding, and configuration of tenant enterprise organizations.
    """

    @classmethod
    async def get_tenant_by_code(cls, db: AsyncSession, code: str) -> Optional[Tenant]:
        query = select(Tenant).where(Tenant.code == code.upper().strip(), Tenant.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def get_tenant_by_id(cls, db: AsyncSession, tenant_id: str) -> Optional[Tenant]:
        query = select(Tenant).where(Tenant.id == tenant_id, Tenant.is_deleted == False)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def provision_tenant(cls, db: AsyncSession, payload: TenantCreate) -> Tenant:
        """Create and initialize a new tenant organization."""
        existing = await cls.get_tenant_by_code(db, payload.code)
        if existing:
            raise EntityAlreadyExistsError(f"Tenant organization with code '{payload.code}' already exists.")

        tenant = Tenant(
            name=payload.name.strip(),
            code=payload.code.upper().strip(),
            currency=payload.currency.upper(),
            tax_identifier=payload.tax_identifier,
            country=payload.country,
            timezone=payload.timezone,
            is_active=True
        )
        db.add(tenant)
        await db.commit()
        await db.refresh(tenant)
        return tenant

    @classmethod
    async def list_tenants(cls, db: AsyncSession) -> List[Tenant]:
        query = select(Tenant).where(Tenant.is_deleted == False).order_by(Tenant.name.asc())
        result = await db.execute(query)
        return list(result.scalars().all())
