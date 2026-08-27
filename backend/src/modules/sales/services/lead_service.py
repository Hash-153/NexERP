"""
NexERP CRM Sales Lead & Pipeline Service.
"""

from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.sales.models import Lead
from backend.src.modules.sales.schemas import LeadCreate
from backend.src.modules.sales.enums import LeadStage


class LeadService:
    """
    CRM Lead opportunity and conversion service.
    """

    @classmethod
    async def generate_lead_number(cls, db: AsyncSession, tenant_id: str) -> str:
        prefix = "LEAD-2026-"
        query = select(Lead).where(Lead.tenant_id == tenant_id).order_by(Lead.lead_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.lead_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_lead(cls, db: AsyncSession, tenant_id: str, payload: LeadCreate) -> Lead:
        lead_num = await cls.generate_lead_number(db, tenant_id)
        lead = Lead(
            tenant_id=tenant_id,
            lead_number=lead_num,
            contact_name=payload.contact_name.strip(),
            company_name=payload.company_name.strip(),
            email=payload.email,
            phone=payload.phone,
            stage=payload.stage.value,
            estimated_value=payload.estimated_value,
            win_probability_percent=payload.win_probability_percent,
            assigned_sales_rep_id=payload.assigned_sales_rep_id,
            source=payload.source,
            notes=payload.notes
        )
        db.add(lead)
        await db.commit()
        await db.refresh(lead)
        return lead

    @classmethod
    async def list_leads(cls, db: AsyncSession, tenant_id: str) -> List[Lead]:
        query = select(Lead).where(Lead.tenant_id == tenant_id, Lead.is_deleted == False).order_by(Lead.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())
