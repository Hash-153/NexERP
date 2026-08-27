"""Manufacturing execution calculations and controlled approvals."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError
from .execution_models import DowntimeEvent, OperatorSession, ProductionQualityCheck, ScrapApproval
from .execution_schemas import DowntimeCreate, OperatorSessionCreate, QualityCheckCreate, ScrapCreate, ScrapDecision


class ManufacturingExecutionService:
    """Records operator output and shop-floor exceptions with audit fields."""

    @staticmethod
    def _hours(start: datetime, end: datetime, break_minutes: int = 0) -> Decimal:
        seconds = (end - start).total_seconds() - break_minutes * 60
        return max(Decimal("0"), Decimal(str(seconds / 3600))).quantize(Decimal("0.01"))

    @classmethod
    async def create_session(cls, db: AsyncSession, tenant_id: str, payload: OperatorSessionCreate) -> OperatorSession:
        ended_at = payload.ended_at or datetime.now(timezone.utc)
        hours = cls._hours(payload.started_at, ended_at, payload.break_minutes)
        session = OperatorSession(tenant_id=tenant_id, productive_hours=hours, labor_cost=hours * payload.hourly_rate, status="COMPLETED" if payload.ended_at else "OPEN", job_card_id=payload.job_card_id, operator_id=payload.operator_id, started_at=payload.started_at, ended_at=payload.ended_at, break_minutes=payload.break_minutes, notes=payload.notes)
        db.add(session)
        await db.commit()
        await db.refresh(session)
        return session

    @classmethod
    async def complete_session(cls, db: AsyncSession, tenant_id: str, session_id: str, hourly_rate: Decimal) -> OperatorSession:
        result = await db.execute(select(OperatorSession).where(OperatorSession.id == session_id, OperatorSession.tenant_id == tenant_id, OperatorSession.is_deleted == False))
        session = result.scalar_one_or_none()
        if not session:
            raise EntityNotFoundError("Operator session not found")
        if session.status != "OPEN":
            raise ValueError("Only open operator sessions can be completed")
        session.ended_at = datetime.now(timezone.utc)
        session.productive_hours = cls._hours(session.started_at, session.ended_at, session.break_minutes)
        session.labor_cost = session.productive_hours * hourly_rate
        session.status = "COMPLETED"
        await db.commit()
        await db.refresh(session)
        return session

    @classmethod
    async def create_quality_check(cls, db: AsyncSession, tenant_id: str, payload: QualityCheckCreate, inspector_id: str) -> ProductionQualityCheck:
        result = "PASS"
        if payload.rejected_quantity > 0:
            result = "FAIL"
        if payload.measurement_value is not None:
            if payload.lower_specification is not None and payload.measurement_value < payload.lower_specification:
                result = "FAIL"
            if payload.upper_specification is not None and payload.measurement_value > payload.upper_specification:
                result = "FAIL"
        check = ProductionQualityCheck(tenant_id=tenant_id, inspector_id=inspector_id, checked_at=datetime.now(timezone.utc), result=result, **payload.model_dump())
        db.add(check)
        await db.commit()
        await db.refresh(check)
        return check

    @classmethod
    async def create_downtime(cls, db: AsyncSession, tenant_id: str, payload: DowntimeCreate, reporter_id: str) -> DowntimeEvent:
        ended_at = payload.ended_at
        duration = int(max(0, (ended_at - payload.started_at).total_seconds() / 60)) if ended_at else 0
        event = DowntimeEvent(tenant_id=tenant_id, reported_by_id=reporter_id, status="CLOSED" if ended_at else "OPEN", duration_minutes=duration, **payload.model_dump())
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @classmethod
    async def close_downtime(cls, db: AsyncSession, tenant_id: str, event_id: str) -> DowntimeEvent:
        result = await db.execute(select(DowntimeEvent).where(DowntimeEvent.id == event_id, DowntimeEvent.tenant_id == tenant_id, DowntimeEvent.is_deleted == False))
        event = result.scalar_one_or_none()
        if not event:
            raise EntityNotFoundError("Downtime event not found")
        if event.status != "OPEN":
            raise ValueError("Only open downtime events can be closed")
        event.ended_at = datetime.now(timezone.utc)
        event.duration_minutes = int((event.ended_at - event.started_at).total_seconds() / 60)
        event.status = "CLOSED"
        await db.commit()
        await db.refresh(event)
        return event

    @classmethod
    async def request_scrap(cls, db: AsyncSession, tenant_id: str, payload: ScrapCreate, requester_id: str) -> ScrapApproval:
        scrap = ScrapApproval(tenant_id=tenant_id, total_cost=payload.quantity * payload.unit_cost, requested_by_id=requester_id, requested_at=datetime.now(timezone.utc), status="PENDING", **payload.model_dump())
        db.add(scrap)
        await db.commit()
        await db.refresh(scrap)
        return scrap

    @classmethod
    async def decide_scrap(cls, db: AsyncSession, tenant_id: str, scrap_id: str, payload: ScrapDecision, approver_id: str) -> ScrapApproval:
        result = await db.execute(select(ScrapApproval).where(ScrapApproval.id == scrap_id, ScrapApproval.tenant_id == tenant_id, ScrapApproval.is_deleted == False))
        scrap = result.scalar_one_or_none()
        if not scrap:
            raise EntityNotFoundError("Scrap approval not found")
        if scrap.status != "PENDING":
            raise ValueError("Only pending scrap requests can be decided")
        scrap.status = payload.status
        scrap.disposition = payload.disposition
        scrap.approved_by_id = approver_id
        scrap.approved_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(scrap)
        return scrap
