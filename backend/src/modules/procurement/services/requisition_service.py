"""
NexERP Purchase Requisition Management Service.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.procurement.models import PurchaseRequisition, PurchaseRequisitionLine
from backend.src.modules.procurement.schemas import RequisitionCreate
from backend.src.modules.procurement.enums import RequisitionStatus


class RequisitionService:
    """
    Purchase Requisition workflow service.
    """

    @classmethod
    async def generate_requisition_number(cls, db: AsyncSession, tenant_id: str, req_date: date) -> str:
        year_str = str(req_date.year)
        prefix = f"PR-{year_str}-"
        query = (
            select(PurchaseRequisition)
            .where(
                PurchaseRequisition.tenant_id == tenant_id,
                PurchaseRequisition.requisition_number.like(f"{prefix}%")
            )
            .order_by(PurchaseRequisition.requisition_number.desc())
            .limit(1)
        )
        res = await db.execute(query)
        latest = res.scalar_one_or_none()
        seq = int(latest.requisition_number.split("-")[-1]) + 1 if latest else 1
        return f"{prefix}{seq:05d}"

    @classmethod
    async def create_requisition(
        cls,
        db: AsyncSession,
        tenant_id: str,
        payload: RequisitionCreate,
        user_id: str
    ) -> PurchaseRequisition:
        req_num = await cls.generate_requisition_number(db, tenant_id, date.today())
        total_est = sum(l.quantity * l.estimated_unit_cost for l in payload.lines)

        pr = PurchaseRequisition(
            tenant_id=tenant_id,
            requisition_number=req_num,
            department_id=payload.department_id,
            requested_by_id=user_id,
            required_by_date=payload.required_by_date,
            status=RequisitionStatus.DRAFT.value,
            estimated_total=total_est,
            justification=payload.justification
        )
        db.add(pr)
        await db.flush()

        for idx, line in enumerate(payload.lines, start=1):
            tot = line.quantity * line.estimated_unit_cost
            pr_line = PurchaseRequisitionLine(
                tenant_id=tenant_id,
                requisition_id=pr.id,
                line_number=idx,
                item_id=line.item_id,
                description=line.description.strip(),
                quantity=line.quantity,
                estimated_unit_cost=line.estimated_unit_cost,
                total_estimated_cost=tot
            )
            db.add(pr_line)

        await db.commit()
        await db.refresh(pr)
        return pr

    @classmethod
    async def approve_requisition(
        cls,
        db: AsyncSession,
        tenant_id: str,
        requisition_id: str,
        user_id: str
    ) -> PurchaseRequisition:
        query = select(PurchaseRequisition).where(
            PurchaseRequisition.id == requisition_id,
            PurchaseRequisition.tenant_id == tenant_id
        )
        res = await db.execute(query)
        pr = res.scalar_one_or_none()
        if not pr:
            raise EntityNotFoundError("Requisition not found.")

        pr.status = RequisitionStatus.APPROVED.value
        pr.approved_by_id = user_id
        pr.approved_at = datetime.now(timezone.utc)

        await db.commit()
        await db.refresh(pr)
        return pr
