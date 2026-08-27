"""
NexERP Shop Floor Control & Job Card Terminal Service.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.manufacturing.models import JobCard, JobCardTimeLog, WorkCenter
from backend.src.modules.manufacturing.schemas import JobCardTimeLogCreate
from backend.src.modules.manufacturing.enums import JobCardStatus


class ShopFloorService:
    """
    Shop Floor operator time logging and ticket status service.
    """

    @classmethod
    async def log_job_card_time(
        cls,
        db: AsyncSession,
        tenant_id: str,
        job_card_id: str,
        payload: JobCardTimeLogCreate,
        operator_id: Optional[str] = None
    ) -> JobCardTimeLog:
        jc_res = await db.execute(
            select(JobCard)
            .where(JobCard.id == job_card_id, JobCard.tenant_id == tenant_id)
            .options(selectinload(JobCard.work_center))
        )
        jc = jc_res.scalar_one_or_none()
        if not jc:
            raise EntityNotFoundError("Job Card not found.")

        # Calculate Labor & Machine cost
        rate = jc.work_center.hourly_rate
        overhead = jc.work_center.overhead_hourly_rate
        labor_cost = payload.duration_hours * rate
        machine_cost = payload.duration_hours * overhead

        time_log = JobCardTimeLog(
            tenant_id=tenant_id,
            job_card_id=jc.id,
            operator_id=operator_id,
            start_time=payload.start_time,
            end_time=payload.end_time,
            duration_hours=payload.duration_hours,
            labor_cost=labor_cost,
            machine_cost=machine_cost
        )
        db.add(time_log)
        jc.status = JobCardStatus.IN_PROGRESS.value

        await db.commit()
        await db.refresh(time_log)
        return time_log

    @classmethod
    async def list_job_cards(cls, db: AsyncSession, tenant_id: str, work_center_id: Optional[str] = None) -> List[JobCard]:
        query = select(JobCard).where(JobCard.tenant_id == tenant_id)
        if work_center_id:
            query = query.where(JobCard.work_center_id == work_center_id)
        query = query.order_by(JobCard.created_at.desc())
        res = await db.execute(query)
        return list(res.scalars().all())
