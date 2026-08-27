"""
NexERP Governance and Workflow Request/Response Pydantic Schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    id: str
    entity_name: str
    entity_id: str
    action_type: str
    user_id: str
    user_email: Optional[str] = None
    created_at: datetime
    changed_fields: Optional[Dict[str, Any]] = None
    entry_hash: str

    class Config:
        from_attributes = True


class WorkflowDefinitionCreate(BaseModel):
    name: str = Field(..., max_length=150)
    document_type: str = Field(..., max_length=50)
    threshold_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    description: Optional[str] = None
    steps: List[Dict[str, Any]] = []


class WorkflowApprovalDecision(BaseModel):
    decision: str = Field(..., description="APPROVED or REJECTED")
    comments: Optional[str] = None
