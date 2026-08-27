"""
NexERP Dynamic Workflow & Approval Matrix Subsystem.
Provides configurable state machines, multi-tiered threshold approvals,
delegation rules, and transition audit trails for enterprise documents.
"""

from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Numeric, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import Base
from .exceptions import WorkflowTransitionError, ApprovalRequiredError, PermissionDeniedError


class WorkflowStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    POSTED = "POSTED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


class ApprovalDecision(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    DELEGATE = "DELEGATE"
    REQUEST_CHANGES = "REQUEST_CHANGES"


class ApprovalRule(Base):
    """
    Configurable approval matrix rule defining threshold limits and required approver roles.
    """
    __tablename__ = "core_approval_rules"

    document_type = Column(String(50), nullable=False, index=True, doc="e.g. PurchaseOrder, ExpenseClaim, JournalEntry")
    min_amount = Column(Numeric(18, 4), default=0.0, nullable=False, doc="Minimum monetary amount triggering rule")
    max_amount = Column(Numeric(18, 4), nullable=True, doc="Maximum monetary amount for this tier")
    required_role = Column(String(50), nullable=False, doc="Role permitted to approve (e.g. DepartmentManager, CFO)")
    tier_level = Column(Integer, default=1, nullable=False, doc="Sequential approval level (1, 2, 3...)")
    department_id = Column(String(36), nullable=True, index=True, doc="Optional department filter")


class ApprovalRequest(Base):
    """
    Pending or historical approval ticket linked to a specific ERP transaction document.
    """
    __tablename__ = "core_approval_requests"

    document_type = Column(String(50), nullable=False, index=True)
    document_id = Column(String(36), nullable=False, index=True)
    tier_level = Column(Integer, default=1, nullable=False)
    required_role = Column(String(50), nullable=False)
    status = Column(String(30), default=WorkflowStatus.PENDING_APPROVAL.value, nullable=False)
    requested_amount = Column(Numeric(18, 4), nullable=True)
    
    assigned_to_user_id = Column(String(36), nullable=True, index=True)
    actioned_by_user_id = Column(String(36), nullable=True)
    decision = Column(String(30), nullable=True)
    comments = Column(Text, nullable=True)
    actioned_at = Column(DateTime(timezone=True), nullable=True)


class WorkflowEngineService:
    """
    Central service managing state transitions, approval chains, and document lifecycles.
    """

    # Allowed state machine transitions per document type
    STATE_MACHINES: Dict[str, Dict[str, List[str]]] = {
        "PurchaseOrder": {
            WorkflowStatus.DRAFT.value: [WorkflowStatus.SUBMITTED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.SUBMITTED.value: [WorkflowStatus.PENDING_APPROVAL.value, WorkflowStatus.APPROVED.value, WorkflowStatus.DRAFT.value],
            WorkflowStatus.PENDING_APPROVAL.value: [WorkflowStatus.APPROVED.value, WorkflowStatus.REJECTED.value],
            WorkflowStatus.APPROVED.value: [WorkflowStatus.IN_PROGRESS.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.IN_PROGRESS.value: [WorkflowStatus.COMPLETED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.COMPLETED.value: [WorkflowStatus.CLOSED.value],
            WorkflowStatus.REJECTED.value: [WorkflowStatus.DRAFT.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.CANCELLED.value: [],
            WorkflowStatus.CLOSED.value: []
        },
        "JournalEntry": {
            WorkflowStatus.DRAFT.value: [WorkflowStatus.SUBMITTED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.SUBMITTED.value: [WorkflowStatus.PENDING_APPROVAL.value, WorkflowStatus.POSTED.value],
            WorkflowStatus.PENDING_APPROVAL.value: [WorkflowStatus.POSTED.value, WorkflowStatus.REJECTED.value],
            WorkflowStatus.POSTED.value: [WorkflowStatus.CANCELLED.value],  # Handled via reversal
            WorkflowStatus.REJECTED.value: [WorkflowStatus.DRAFT.value],
            WorkflowStatus.CANCELLED.value: []
        },
        "SalesOrder": {
            WorkflowStatus.DRAFT.value: [WorkflowStatus.SUBMITTED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.SUBMITTED.value: [WorkflowStatus.APPROVED.value, WorkflowStatus.PENDING_APPROVAL.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.PENDING_APPROVAL.value: [WorkflowStatus.APPROVED.value, WorkflowStatus.REJECTED.value],
            WorkflowStatus.APPROVED.value: [WorkflowStatus.IN_PROGRESS.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.IN_PROGRESS.value: [WorkflowStatus.COMPLETED.value],
            WorkflowStatus.COMPLETED.value: [WorkflowStatus.CLOSED.value],
            WorkflowStatus.CANCELLED.value: []
        },
        "ProductionOrder": {
            WorkflowStatus.DRAFT.value: [WorkflowStatus.APPROVED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.APPROVED.value: [WorkflowStatus.IN_PROGRESS.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.IN_PROGRESS.value: [WorkflowStatus.COMPLETED.value, WorkflowStatus.CANCELLED.value],
            WorkflowStatus.COMPLETED.value: [WorkflowStatus.CLOSED.value],
            WorkflowStatus.CANCELLED.value: []
        }
    }

    @classmethod
    def validate_transition(cls, document_type: str, current_state: str, target_state: str) -> None:
        """
        Validate whether a requested state transition is permissible according to the workflow graph.
        """
        machine = cls.STATE_MACHINES.get(document_type)
        if not machine:
            # If document type has no strict machine, allow standard flow
            return

        allowed_targets = machine.get(current_state, [])
        if target_state not in allowed_targets:
            raise WorkflowTransitionError(
                message=f"Cannot transition {document_type} from '{current_state}' to '{target_state}'. Allowed: {allowed_targets}",
                details={
                    "document_type": document_type,
                    "current_state": current_state,
                    "target_state": target_state,
                    "allowed_targets": allowed_targets
                }
            )

    @classmethod
    async def evaluate_approval_requirement(
        cls,
        db: AsyncSession,
        tenant_id: str,
        document_type: str,
        document_id: str,
        amount: Optional[float] = 0.0,
        department_id: Optional[str] = None
    ) -> Optional[ApprovalRequest]:
        """
        Check configured approval rules and create approval ticket if thresholds are met.
        """
        query = (
            select(ApprovalRule)
            .where(
                ApprovalRule.tenant_id == tenant_id,
                ApprovalRule.document_type == document_type,
                ApprovalRule.is_active == True,
                ApprovalRule.min_amount <= amount
            )
            .order_by(ApprovalRule.tier_level.asc())
        )
        
        result = await db.execute(query)
        rules = result.scalars().all()

        if not rules:
            return None

        first_rule = rules[0]
        request = ApprovalRequest(
            tenant_id=tenant_id,
            document_type=document_type,
            document_id=document_id,
            tier_level=first_rule.tier_level,
            required_role=first_rule.required_role,
            status=WorkflowStatus.PENDING_APPROVAL.value,
            requested_amount=amount
        )
        db.add(request)
        await db.flush()
        return request

    @classmethod
    async def process_decision(
        cls,
        db: AsyncSession,
        request_id: str,
        decision: ApprovalDecision,
        user_id: str,
        user_roles: List[str],
        comments: Optional[str] = None
    ) -> ApprovalRequest:
        """
        Record manager approval or rejection for a document ticket.
        """
        query = select(ApprovalRequest).where(ApprovalRequest.id == request_id)
        result = await db.execute(query)
        req = result.scalar_one_or_none()

        if not req:
            raise WorkflowTransitionError("Approval request ticket not found.")

        if req.status != WorkflowStatus.PENDING_APPROVAL.value:
            raise WorkflowTransitionError(f"Approval request is already in status: {req.status}")

        if req.required_role not in user_roles and "SuperAdmin" not in user_roles:
            raise PermissionDeniedError(
                f"You do not possess the required role '{req.required_role}' to approve this document."
            )

        req.decision = decision.value
        req.actioned_by_user_id = user_id
        req.actioned_at = datetime.now(timezone.utc)
        req.comments = comments

        if decision == ApprovalDecision.APPROVE:
            req.status = WorkflowStatus.APPROVED.value
        elif decision == ApprovalDecision.REJECT:
            req.status = WorkflowStatus.REJECTED.value

        await db.flush()
        return req
