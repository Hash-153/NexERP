"""
NexERP Multi-Tier Approval Workflow Engine & Delegation of Authority Matrix.
Evaluates dollar authorization limits, dispatches approval requests to role inboxes,
and manages sequential multi-tier sign-offs.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.exceptions import EntityNotFoundError, BusinessRuleViolationError
from backend.src.modules.governance.models import (
    WorkflowDefinition,
    WorkflowStepDefinition,
    WorkflowInstance,
    WorkflowApprovalAction
)
from backend.src.modules.governance.enums import WorkflowStatus, ApprovalDecision


class WorkflowEngineService:
    """
    Delegation of Authority & Multi-Tier Approval Workflow Engine.
    """

    @classmethod
    async def initiate_approval_workflow(
        cls,
        db: AsyncSession,
        tenant_id: str,
        document_type: str,
        document_id: str,
        document_reference: str,
        transaction_amount: Decimal,
        requested_by_id: str
    ) -> Optional[WorkflowInstance]:
        """
        Check if transaction amount exceeds defined workflow thresholds; if so, launch approval lifecycle.
        """
        # Find active workflow definition for document type
        query = (
            select(WorkflowDefinition)
            .where(
                WorkflowDefinition.tenant_id == tenant_id,
                WorkflowDefinition.document_type == document_type,
                WorkflowDefinition.is_active == True,
                WorkflowDefinition.threshold_amount <= transaction_amount
            )
            .options(selectinload(WorkflowDefinition.steps))
            .order_by(WorkflowDefinition.threshold_amount.desc())
            .limit(1)
        )
        res = await db.execute(query)
        wf_def = res.scalar_one_or_none()

        if not wf_def or not wf_def.steps:
            # No approval needed (auto-approved / below threshold)
            return None

        instance = WorkflowInstance(
            tenant_id=tenant_id,
            workflow_id=wf_def.id,
            document_type=document_type,
            document_id=document_id,
            document_reference=document_reference,
            transaction_amount=transaction_amount,
            requested_by_id=requested_by_id,
            status=WorkflowStatus.IN_PROGRESS.value,
            current_step_number=Decimal("1")
        )
        db.add(instance)
        await db.flush()

        # Create first step action
        first_step = sorted(wf_def.steps, key=lambda s: s.step_number)[0]
        action = WorkflowApprovalAction(
            tenant_id=tenant_id,
            instance_id=instance.id,
            step_number=first_step.step_number,
            approver_id=first_step.required_role_name,
            decision=ApprovalDecision.PENDING.value
        )
        db.add(action)
        await db.commit()
        await db.refresh(instance)
        return instance

    @classmethod
    async def process_approval_decision(
        cls,
        db: AsyncSession,
        tenant_id: str,
        instance_id: str,
        approver_id: str,
        decision: str,
        comments: Optional[str] = None
    ) -> WorkflowInstance:
        """
        Process approver decision (APPROVED / REJECTED) and transition workflow to next tier or final status.
        """
        query = (
            select(WorkflowInstance)
            .where(WorkflowInstance.id == instance_id, WorkflowInstance.tenant_id == tenant_id)
            .options(
                selectinload(WorkflowInstance.approval_actions),
                selectinload(WorkflowInstance.workflow).selectinload(WorkflowDefinition.steps)
            )
        )
        res = await db.execute(query)
        instance = res.scalar_one_or_none()
        if not instance:
            raise EntityNotFoundError("Workflow instance not found.")

        if instance.status != WorkflowStatus.IN_PROGRESS.value:
            raise BusinessRuleViolationError(f"Workflow instance is already {instance.status}.")

        if decision == ApprovalDecision.REJECTED.value:
            instance.status = WorkflowStatus.REJECTED.value
            action = WorkflowApprovalAction(
                tenant_id=tenant_id,
                instance_id=instance.id,
                step_number=instance.current_step_number,
                approver_id=approver_id,
                decision=ApprovalDecision.REJECTED.value,
                decision_at=datetime.now(timezone.utc),
                comments=comments
            )
            db.add(action)
            await db.commit()
            await db.refresh(instance)
            return instance

        # Record Approval
        action = WorkflowApprovalAction(
            tenant_id=tenant_id,
            instance_id=instance.id,
            step_number=instance.current_step_number,
            approver_id=approver_id,
            decision=ApprovalDecision.APPROVED.value,
            decision_at=datetime.now(timezone.utc),
            comments=comments
        )
        db.add(action)

        # Check for subsequent steps
        steps = sorted(instance.workflow.steps, key=lambda s: s.step_number)
        current_step_num = int(instance.current_step_number)
        next_steps = [s for s in steps if s.step_number > current_step_num]

        if next_steps:
            next_step = next_steps[0]
            instance.current_step_number = next_step.step_number
            next_action = WorkflowApprovalAction(
                tenant_id=tenant_id,
                instance_id=instance.id,
                step_number=next_step.step_number,
                approver_id=next_step.required_role_name,
                decision=ApprovalDecision.PENDING.value
            )
            db.add(next_action)
        else:
            # Final approval step completed
            instance.status = WorkflowStatus.APPROVED.value

        await db.commit()
        await db.refresh(instance)
        return instance
