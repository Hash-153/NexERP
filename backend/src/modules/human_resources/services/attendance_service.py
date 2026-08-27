"""
NexERP Attendance & Shift Tracking Service.
"""

from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.modules.human_resources.models import AttendanceLog
from backend.src.modules.human_resources.schemas import AttendanceLogCreate


class AttendanceService:
    """
    Biometric punch and daily work attendance manager.
    """

    @classmethod
    async def log_attendance(cls, db: AsyncSession, tenant_id: str, payload: AttendanceLogCreate) -> AttendanceLog:
        log = AttendanceLog(
            tenant_id=tenant_id,
            employee_id=payload.employee_id,
            punch_date=payload.punch_date,
            check_in_time=payload.check_in_time,
            check_out_time=payload.check_out_time,
            hours_worked=payload.hours_worked,
            overtime_hours=payload.overtime_hours,
            status=payload.status.value
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @classmethod
    async def list_attendance(cls, db: AsyncSession, tenant_id: str, employee_id: Optional[str] = None) -> List[AttendanceLog]:
        query = select(AttendanceLog).where(AttendanceLog.tenant_id == tenant_id)
        if employee_id:
            query = query.where(AttendanceLog.employee_id == employee_id)
        query = query.order_by(AttendanceLog.punch_date.desc())
        res = await db.execute(query)
        return list(res.scalars().all())
