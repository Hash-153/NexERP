"""
NexERP Employee Timesheet & Billable Costing Service.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError
from backend.src.modules.projects.models import Timesheet, TimesheetEntry, Project, Task
from backend.src.modules.projects.schemas import TimesheetCreate
from backend.src.modules.projects.enums import TimesheetStatus


class TimesheetService:
    """
    Weekly timesheet submission and project cost allocation service.
    """

    @classmethod
    async def log_timesheet(cls, db: AsyncSession, tenant_id: str, payload: TimesheetCreate) -> Timesheet:
        ts_num = f"TS-{payload.period_start_date.strftime('%Y%m%d')}-{payload.employee_id[:6]}"
        total_h = sum(e.hours for e in payload.entries)

        ts = Timesheet(
            tenant_id=tenant_id,
            timesheet_number=ts_num,
            employee_id=payload.employee_id,
            period_start_date=payload.period_start_date,
            period_end_date=payload.period_end_date,
            total_hours=total_h,
            status=TimesheetStatus.SUBMITTED.value
        )
        db.add(ts)
        await db.flush()

        for entry in payload.entries:
            e = TimesheetEntry(
                tenant_id=tenant_id,
                timesheet_id=ts.id,
                project_id=entry.project_id,
                task_id=entry.task_id,
                work_date=entry.work_date,
                hours=entry.hours,
                hourly_billing_rate=entry.hourly_billing_rate,
                is_billable=entry.is_billable,
                description=entry.description
            )
            db.add(e)

            # Update project hours
            p_res = await db.execute(select(Project).where(Project.id == entry.project_id))
            prj = p_res.scalar_one_or_none()
            if prj:
                prj.total_logged_hours += entry.hours
                prj.total_cost_incurred += (entry.hours * entry.hourly_billing_rate)

            # Update task actual hours
            if entry.task_id:
                t_res = await db.execute(select(Task).where(Task.id == entry.task_id))
                tsk = t_res.scalar_one_or_none()
                if tsk:
                    tsk.actual_hours += entry.hours

        await db.commit()
        await db.refresh(ts)
        return ts

    @classmethod
    async def list_timesheets(cls, db: AsyncSession, tenant_id: str, employee_id: Optional[str] = None) -> List[Timesheet]:
        query = (
            select(Timesheet)
            .where(Timesheet.tenant_id == tenant_id, Timesheet.is_deleted == False)
            .options(selectinload(Timesheet.entries))
            .order_by(Timesheet.period_start_date.desc())
        )
        if employee_id:
            query = query.where(Timesheet.employee_id == employee_id)
        res = await db.execute(query)
        return list(res.scalars().all())
