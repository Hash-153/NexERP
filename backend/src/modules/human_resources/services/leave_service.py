"""
NexERP Leave Management & Accrual Policy Service.
"""

from datetime import date, datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, InsufficientLeaveBalanceError
from backend.src.modules.human_resources.models import LeaveType, LeaveRequest
from backend.src.modules.human_resources.schemas import LeaveTypeCreate, LeaveRequestCreate
from backend.src.modules.human_resources.enums import LeaveStatus


class LeaveService:
    """
    Leave application, approval, and balance management service.
    """

    @classmethod
    async def create_leave_type(cls, db: AsyncSession, tenant_id: str, payload: LeaveTypeCreate) -> LeaveType:
        lt = LeaveType(
            tenant_id=tenant_id,
            code=payload.code.upper().strip(),
            name=payload.name.strip(),
            annual_allowance_days=payload.annual_allowance_days,
            is_carry_forward=payload.is_carry_forward,
            max_carry_forward_days=payload.max_carry_forward_days,
            is_paid=payload.is_paid
        )
        db.add(lt)
        await db.commit()
        await db.refresh(lt)
        return lt

    @classmethod
    async def list_leave_types(cls, db: AsyncSession) -> List[LeaveType]:
        res = await db.execute(select(LeaveType).order_by(LeaveType.name.asc()))
        return list(res.scalars().all())

    @classmethod
    async def submit_leave_request(cls, db: AsyncSession, tenant_id: str, payload: LeaveRequestCreate) -> LeaveRequest:
        req = LeaveRequest(
            tenant_id=tenant_id,
            employee_id=payload.employee_id,
            leave_type_id=payload.leave_type_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            total_days=payload.total_days,
            reason=payload.reason,
            status=LeaveStatus.SUBMITTED.value
        )
        db.add(req)
        await db.commit()
        await db.refresh(req)
        return req

    @classmethod
    async def approve_leave_request(
        cls,
        db: AsyncSession,
        tenant_id: str,
        request_id: str,
        approver_id: str
    ) -> LeaveRequest:
        res = await db.execute(select(LeaveRequest).where(LeaveRequest.id == request_id, LeaveRequest.tenant_id == tenant_id))
        req = res.scalar_one_or_none()
        if not req:
            raise EntityNotFoundError("Leave request not found.")

        req.status = LeaveStatus.APPROVED.value
        req.approved_by_id = approver_id
        req.approved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(req)
        return req

    @classmethod
    async def list_leave_requests(cls, db: AsyncSession, tenant_id: str, employee_id: Optional[str] = None) -> List[LeaveRequest]:
        query = (
            select(LeaveRequest)
            .where(LeaveRequest.tenant_id == tenant_id, LeaveRequest.is_deleted == False)
            .options(
                selectinload(LeaveRequest.leave_type),
                selectinload(LeaveRequest.employee)
            )
            .order_by(LeaveRequest.start_date.desc())
        )
        if employee_id:
            query = query.where(LeaveRequest.employee_id == employee_id)
        res = await db.execute(query)
        return list(res.scalars().all())
