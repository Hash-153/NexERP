"""
NexERP Non-Conformance Reports (NCR) & CAPA Resolution Service.
"""

from datetime import datetime, timezone, date
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.quality_control.models import NonConformanceReport
from backend.src.modules.quality_control.schemas import NCRCreate
from backend.src.modules.quality_control.enums import NCRStatus


class NCRService:
    """
    Non-Conformance Report (NCR) and corrective action workflow service.
    """

    @classmethod
    async def generate_ncr_number(cls, db: AsyncSession, tenant_id: str) -> str:
        year_str = str(date.today().year)
        prefix = f"NCR-{year_str}-"
        query = select(NonConformanceReport).where(NonConformanceReport.tenant_id == tenant_id).order_by(NonConformanceReport.ncr_number.desc()).limit(1)
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.ncr_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def file_ncr(cls, db: AsyncSession, tenant_id: str, payload: NCRCreate) -> NonConformanceReport:
        ncr_num = await cls.generate_ncr_number(db, tenant_id)
        ncr = NonConformanceReport(
            tenant_id=tenant_id,
            ncr_number=ncr_num,
            inspection_record_id=payload.inspection_record_id,
            item_id=payload.item_id,
            issue_summary=payload.issue_summary.strip(),
            root_cause_analysis=payload.root_cause_analysis,
            containment_action=payload.containment_action,
            corrective_action=payload.corrective_action,
            status=NCRStatus.OPEN.value,
            assigned_to_id=payload.assigned_to_id
        )
        db.add(ncr)
        await db.commit()
        await db.refresh(ncr)
        return ncr

    @classmethod
    async def close_ncr(cls, db: AsyncSession, tenant_id: str, ncr_id: str) -> NonConformanceReport:
        query = select(NonConformanceReport).where(NonConformanceReport.id == ncr_id, NonConformanceReport.tenant_id == tenant_id)
        res = await db.execute(query)
        ncr = res.scalar_one_or_none()
        if not ncr:
            raise EntityNotFoundError("NCR record not found.")

        ncr.status = NCRStatus.CLOSED.value
        ncr.closed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(ncr)
        return ncr

    @classmethod
    async def list_ncrs(cls, db: AsyncSession, tenant_id: str) -> List[NonConformanceReport]:
        query = select(NonConformanceReport).where(NonConformanceReport.tenant_id == tenant_id, NonConformanceReport.is_deleted == False).order_by(NonConformanceReport.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())
