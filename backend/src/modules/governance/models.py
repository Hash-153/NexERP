"""
NexERP Governance, Risk & Compliance (GRC), SOX Audit Trail and Workflow Models.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Numeric, JSON
from sqlalchemy.orm import relationship

from backend.src.core.database import Base
from backend.src.modules.governance.enums import AuditActionType, WorkflowStatus, ApprovalDecision


class AuditLog(Base):
    """
    Immutable SOX Section 404 audit log tracking every data mutation and financial posting.
    Includes SHA-256 cryptographic chaining hash to ensure tamper-evidence.
    """
    __tablename__ = "grc_audit_logs"

    entity_name = Column(String(100), nullable=False, index=True, doc="e.g. JournalEntry, SalesInvoice, PurchaseOrder")
    entity_id = Column(String(50), nullable=False, index=True)
    action_type = Column(String(50), default=AuditActionType.UPDATE.value, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    user_email = Column(String(255), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    changed_fields = Column(JSON, nullable=True, doc="Dictionary of before/after delta values")
    previous_hash = Column(String(64), nullable=True, doc="SHA-256 hash of previous block")
    entry_hash = Column(String(64), nullable=False, doc="SHA-256 cryptographic verification checksum")


class WorkflowDefinition(Base):
    """
    Configurable approval matrix rule (e.g. Purchase Orders > $50k require CFO sign-off).
    """
    __tablename__ = "grc_workflow_definitions"

    name = Column(String(150), nullable=False)
    document_type = Column(String(50), nullable=False, index=True, doc="e.g. PurchaseOrder, JournalEntry, ExpenseClaim")
    threshold_amount = Column(Numeric(18, 2), default=0.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    description = Column(String(255), nullable=True)

    steps = relationship("WorkflowStepDefinition", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStepDefinition(Base):
    """
    Sequential tier in approval workflow with required role or designated approver.
    """
    __tablename__ = "grc_workflow_step_definitions"

    workflow_id = Column(String(36), ForeignKey("grc_workflow_definitions.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Numeric(4, 0), default=1, nullable=False)
    required_role_name = Column(String(100), nullable=False)
    auto_escalate_hours = Column(Numeric(6, 0), default=48, nullable=False)

    workflow = relationship("WorkflowDefinition", back_populates="steps")


class WorkflowInstance(Base):
    """
    Active approval execution lifecycle instance tied to a business transaction.
    """
    __tablename__ = "grc_workflow_instances"

    workflow_id = Column(String(36), ForeignKey("grc_workflow_definitions.id"), nullable=False)
    document_type = Column(String(50), nullable=False)
    document_id = Column(String(50), nullable=False, index=True)
    document_reference = Column(String(100), nullable=True)
    transaction_amount = Column(Numeric(18, 2), default=0.0, nullable=False)
    requested_by_id = Column(String(50), nullable=False)
    status = Column(String(30), default=WorkflowStatus.IN_PROGRESS.value, nullable=False)
    current_step_number = Column(Numeric(4, 0), default=1, nullable=False)

    workflow = relationship("WorkflowDefinition")
    approval_actions = relationship("WorkflowApprovalAction", back_populates="instance", cascade="all, delete-orphan")


class WorkflowApprovalAction(Base):
    """
    Individual approver voting record with timestamp and digital signature remarks.
    """
    __tablename__ = "grc_workflow_approval_actions"

    instance_id = Column(String(36), ForeignKey("grc_workflow_instances.id", ondelete="CASCADE"), nullable=False)
    step_number = Column(Numeric(4, 0), nullable=False)
    approver_id = Column(String(50), nullable=False)
    decision = Column(String(30), default=ApprovalDecision.PENDING.value, nullable=False)
    decision_at = Column(DateTime(timezone=True), nullable=True)
    comments = Column(Text, nullable=True)

    instance = relationship("WorkflowInstance", back_populates="approval_actions")
