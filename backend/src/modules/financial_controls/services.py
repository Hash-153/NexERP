"""Financial close, approval, cash forecasting, and reconciliation services."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.financials.models import FiscalPeriod
from .models import ApprovalPolicy, ApprovalRequest, CashForecastLine, CloseChecklist, ReconciliationException
from .schemas import ApprovalDecision, ApprovalPolicyCreate, ApprovalRequestCreate, CashForecastCreate, ChecklistComplete, CloseChecklistCreate, ReconciliationExceptionCreate, ReconciliationResolution


class FinancialControlService:
    """Provides controlled close and approval workflows around the general ledger."""

    @staticmethod
    async def period(db: AsyncSession, tenant_id: str, period_id: str) -> FiscalPeriod:
        result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.id == period_id, FiscalPeriod.tenant_id == tenant_id))
        period = result.scalar_one_or_none()
        if not period:
            raise EntityNotFoundError("Fiscal period not found")
        return period

    @classmethod
    async def add_checklist_item(cls, db: AsyncSession, tenant_id: str, payload: CloseChecklistCreate) -> CloseChecklist:
        await cls.period(db, tenant_id, payload.period_id)
        item = CloseChecklist(tenant_id=tenant_id, status="OPEN", **payload.model_dump())
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return item

    @classmethod
    async def complete_checklist_item(cls, db: AsyncSession, tenant_id: str, item_id: str, payload: ChecklistComplete, user_id: str) -> CloseChecklist:
        result = await db.execute(select(CloseChecklist).where(CloseChecklist.id == item_id, CloseChecklist.tenant_id == tenant_id, CloseChecklist.is_deleted == False))
        item = result.scalar_one_or_none()
        if not item:
            raise EntityNotFoundError("Close checklist item not found")
        item.completed = True
        item.status = "COMPLETED"
        item.completed_at = datetime.now(timezone.utc)
        item.completed_by_id = user_id
        item.evidence_reference = payload.evidence_reference
        item.exception_note = payload.exception_note
        await db.commit()
        await db.refresh(item)
        return item

    @classmethod
    async def readiness(cls, db: AsyncSession, tenant_id: str, period_id: str) -> dict:
        await cls.period(db, tenant_id, period_id)
        result = await db.execute(select(CloseChecklist.completed).where(CloseChecklist.tenant_id == tenant_id, CloseChecklist.period_id == period_id, CloseChecklist.required == True, CloseChecklist.is_deleted == False))
        completion_flags = list(result.scalars().all())
        required = len(completion_flags)
        completed = sum(1 for completed_flag in completion_flags if completed_flag)
        return {"period_id": period_id, "required_count": required, "completed_count": completed, "open_required_count": required - completed, "ready_to_lock": required == completed}

    @classmethod
    async def lock_period(cls, db: AsyncSession, tenant_id: str, period_id: str) -> FiscalPeriod:
        period = await cls.period(db, tenant_id, period_id)
        readiness = await cls.readiness(db, tenant_id, period_id)
        if not readiness["ready_to_lock"]:
            raise BusinessRuleViolationError("Cannot lock period while required close controls remain open")
        period.is_locked = True
        await db.commit()
        await db.refresh(period)
        return period

    @classmethod
    async def create_policy(cls, db: AsyncSession, tenant_id: str, payload: ApprovalPolicyCreate) -> ApprovalPolicy:
        policy = ApprovalPolicy(tenant_id=tenant_id, active=True, **payload.model_dump())
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
        return policy

    @classmethod
    async def request_approval(cls, db: AsyncSession, tenant_id: str, payload: ApprovalRequestCreate, user_id: str) -> ApprovalRequest:
        result = await db.execute(select(ApprovalPolicy).where(ApprovalPolicy.tenant_id == tenant_id, ApprovalPolicy.document_type == payload.document_type, ApprovalPolicy.active == True, ApprovalPolicy.minimum_amount <= payload.amount, (ApprovalPolicy.maximum_amount.is_(None) | (ApprovalPolicy.maximum_amount >= payload.amount))).order_by(ApprovalPolicy.approval_level.asc()))
        policy = result.scalars().first()
        if not policy:
            raise EntityNotFoundError("No active approval policy matches this document amount")
        previous = await db.execute(select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id).order_by(ApprovalRequest.request_number.desc()).limit(1))
        latest = previous.scalar_one_or_none()
        sequence = 1
        if latest:
            try:
                sequence = int(latest.request_number.rsplit("-", 1)[1]) + 1
            except (ValueError, IndexError):
                pass
        request = ApprovalRequest(tenant_id=tenant_id, request_number=f"APR-{datetime.now(timezone.utc).year}-{sequence:05d}", requested_by_id=user_id, policy_id=policy.id, approval_level=policy.approval_level, status="PENDING", **payload.model_dump())
        db.add(request)
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def decide_approval(cls, db: AsyncSession, tenant_id: str, request_id: str, payload: ApprovalDecision, user_id: str) -> ApprovalRequest:
        result = await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == request_id, ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.is_deleted == False))
        request = result.scalar_one_or_none()
        if not request:
            raise EntityNotFoundError("Approval request not found")
        if request.status != "PENDING":
            raise ValueError("Only pending approval requests can be decided")
        request.status = payload.status
        request.decided_by_id = user_id
        request.decided_at = datetime.now(timezone.utc)
        request.decision_note = payload.decision_note
        await db.commit()
        await db.refresh(request)
        return request

    @classmethod
    async def add_cash_line(cls, db: AsyncSession, tenant_id: str, payload: CashForecastCreate) -> CashForecastLine:
        line = CashForecastLine(tenant_id=tenant_id, status="OPEN", **payload.model_dump())
        db.add(line)
        await db.commit()
        await db.refresh(line)
        return line

    @classmethod
    async def cash_summary(cls, db: AsyncSession, tenant_id: str) -> dict:
        result = await db.execute(select(CashForecastLine.forecast_type, func.coalesce(func.sum(CashForecastLine.expected_amount * CashForecastLine.probability_percent / 100), 0)).where(CashForecastLine.tenant_id == tenant_id, CashForecastLine.status == "OPEN").group_by(CashForecastLine.forecast_type))
        values = {kind: amount for kind, amount in result.all()}
        inflow = values.get("INFLOW", Decimal("0"))
        outflow = values.get("OUTFLOW", Decimal("0"))
        return {"weighted_inflow": inflow, "weighted_outflow": outflow, "weighted_net_cash": inflow - outflow}

    @classmethod
    async def create_reconciliation_exception(cls, db: AsyncSession, tenant_id: str, payload: ReconciliationExceptionCreate) -> ReconciliationException:
        exception = ReconciliationException(tenant_id=tenant_id, variance_amount=payload.statement_amount - payload.book_amount, status="OPEN", **payload.model_dump())
        db.add(exception)
        await db.commit()
        await db.refresh(exception)
        return exception

    @classmethod
    async def resolve_reconciliation_exception(cls, db: AsyncSession, tenant_id: str, exception_id: str, payload: ReconciliationResolution, user_id: str) -> ReconciliationException:
        result = await db.execute(select(ReconciliationException).where(ReconciliationException.id == exception_id, ReconciliationException.tenant_id == tenant_id, ReconciliationException.is_deleted == False))
        exception = result.scalar_one_or_none()
        if not exception:
            raise EntityNotFoundError("Reconciliation exception not found")
        if exception.status != "OPEN":
            raise ValueError("Only open reconciliation exceptions can be resolved")
        exception.status = "RESOLVED"
        exception.resolution_note = payload.resolution_note
        exception.resolved_by_id = user_id
        exception.resolved_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(exception)
        return exception
