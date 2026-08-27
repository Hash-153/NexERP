"""
NexERP Governance, Risk, Compliance & Audit API Endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from backend.src.modules.auth.models import User
from backend.src.modules.governance.schemas import AuditLogResponse, WorkflowApprovalDecision
from backend.src.modules.governance.services.audit_trail_service import AuditTrailService
from backend.src.modules.governance.services.workflow_engine_service import WorkflowEngineService

router = APIRouter(prefix="/governance", tags=["Governance, Risk & Compliance"])


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_trail_logs(
    entity_name: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Retrieve immutable SOX audit trail logs for tenant."""
    return await AuditTrailService.list_audit_trail(
        db, current_user.tenant_id, entity_name, entity_id, limit
    )


@router.post("/workflows/{instance_id}/decision")
async def submit_workflow_approval_decision(
    instance_id: str,
    payload: WorkflowApprovalDecision,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Process an approval or rejection decision on an active workflow."""
    return await WorkflowEngineService.process_approval_decision(
        db=db,
        tenant_id=current_user.tenant_id,
        instance_id=instance_id,
        approver_id=current_user.id,
        decision=payload.decision,
        comments=payload.comments
    )
