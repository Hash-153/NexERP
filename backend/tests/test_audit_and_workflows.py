"""
NexERP Cryptographic Audit Trail & Approval Workflow Test Suite.
"""

from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.modules.governance.models import WorkflowDefinition, WorkflowStepDefinition
from backend.src.modules.governance.services import AuditTrailService, WorkflowEngineService
from backend.src.modules.governance.enums import WorkflowStatus, ApprovalDecision


@pytest.mark.asyncio
async def test_cryptographic_audit_trail_hash_chaining(db_session: AsyncSession):
    """
    Ensure each audit log entry cryptographically incorporates the hash of the preceding entry.
    """
    tenant_id = "org_corp_hq_001"

    # Log entry 1
    log1 = await AuditTrailService.log_mutation(
        db=db_session,
        tenant_id=tenant_id,
        entity_name="JournalEntry",
        entity_id="JV-1001",
        action_type="POST_TRANSACTION",
        user_id="user_admin",
        changed_fields={"status": "POSTED"}
    )
    assert log1.entry_hash is not None

    # Log entry 2
    log2 = await AuditTrailService.log_mutation(
        db=db_session,
        tenant_id=tenant_id,
        entity_name="JournalEntry",
        entity_id="JV-1002",
        action_type="POST_TRANSACTION",
        user_id="user_admin",
        changed_fields={"status": "POSTED"}
    )
    assert log2.previous_hash == log1.entry_hash


@pytest.mark.asyncio
async def test_multi_tier_workflow_approval_execution(db_session: AsyncSession):
    """
    Ensure multi-tier PO approval progresses through defined authorization steps.
    """
    tenant_id = "org_corp_hq_001"

    # Define Workflow: POs > $10,000 require Step 1 (PurchasingManager) -> Step 2 (CFO)
    wf = WorkflowDefinition(
        tenant_id=tenant_id,
        name="CapEx Purchase Order Approval",
        document_type="PurchaseOrder",
        threshold_amount=Decimal("10000.00"),
        is_active=True
    )
    db_session.add(wf)
    await db_session.flush()

    s1 = WorkflowStepDefinition(tenant_id=tenant_id, workflow_id=wf.id, step_number=1, required_role_name="PurchasingManager")
    s2 = WorkflowStepDefinition(tenant_id=tenant_id, workflow_id=wf.id, step_number=2, required_role_name="CFO")
    db_session.add_all([s1, s2])
    await db_session.commit()

    # Initiate workflow for $25,000 PO
    instance = await WorkflowEngineService.initiate_approval_workflow(
        db=db_session,
        tenant_id=tenant_id,
        document_type="PurchaseOrder",
        document_id="PO-9901",
        document_reference="PO-9901",
        transaction_amount=Decimal("25000.00"),
        requested_by_id="buyer_user"
    )
    assert instance is not None
    assert instance.status == WorkflowStatus.IN_PROGRESS.value
    assert instance.current_step_number == 1

    # Step 1 Approval by Purchasing Manager
    inst_step1 = await WorkflowEngineService.process_approval_decision(
        db=db_session,
        tenant_id=tenant_id,
        instance_id=instance.id,
        approver_id="mgr_user",
        decision=ApprovalDecision.APPROVED.value,
        comments="Approved budget availability"
    )
    assert inst_step1.status == WorkflowStatus.IN_PROGRESS.value
    assert inst_step1.current_step_number == 2

    # Step 2 Approval by CFO
    inst_step2 = await WorkflowEngineService.process_approval_decision(
        db=db_session,
        tenant_id=tenant_id,
        instance_id=instance.id,
        approver_id="cfo_user",
        decision=ApprovalDecision.APPROVED.value,
        comments="Approved expenditure"
    )
    assert inst_step2.status == WorkflowStatus.APPROVED.value
