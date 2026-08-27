"""
NexERP Work Center & Plant Capacity Service.
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.exceptions import EntityAlreadyExistsError, EntityNotFoundError
from backend.src.modules.manufacturing.models import WorkCenter
from backend.src.modules.manufacturing.schemas import WorkCenterCreate


class WorkCenterService:
    """
    Work center machine and labor resource manager.
    """

    @classmethod
    async def create_work_center(cls, db: AsyncSession, tenant_id: str, payload: WorkCenterCreate) -> WorkCenter:
        query = select(WorkCenter).where(
            WorkCenter.tenant_id == tenant_id,
            WorkCenter.code == payload.code.upper().strip(),
            WorkCenter.is_deleted == False
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise EntityAlreadyExistsError(f"Work center '{payload.code}' already exists.")

        wc = WorkCenter(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            work_center_type=payload.work_center_type.value,
            hourly_rate=payload.hourly_rate,
            overhead_hourly_rate=payload.overhead_hourly_rate,
            capacity_hours_per_day=payload.capacity_hours_per_day,
            efficiency_percentage=payload.efficiency_percentage
        )
        db.add(wc)
        await db.commit()
        await db.refresh(wc)
        return wc

    @classmethod
    async def list_work_centers(cls, db: AsyncSession, tenant_id: str) -> List[WorkCenter]:
        query = select(WorkCenter).where(WorkCenter.tenant_id == tenant_id, WorkCenter.is_deleted == False).order_by(WorkCenter.code.asc())
        res = await db.execute(query)
        return list(res.scalars().all())
