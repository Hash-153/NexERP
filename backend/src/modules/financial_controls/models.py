"""Audit-ready financial control persistence models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from backend.src.core.database import Base


class CloseChecklist(Base):
    __tablename__ = "fc_close_checklists"
    __table_args__ = (Index("ix_fc_close_tenant_period", "tenant_id", "period_id"),)
    period_id = Column(String(36), ForeignKey("fin_fiscal_periods.id"), nullable=False)
    checklist_code = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    owner_id = Column(String(36), nullable=True)
    required = Column(Boolean, nullable=False, default=True)
    completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    completed_by_id = Column(String(36), nullable=True)
    evidence_reference = Column(String(255), nullable=True)
    exception_note = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")


class ApprovalPolicy(Base):
    __tablename__ = "fc_approval_policies"
    document_type = Column(String(50), nullable=False)
    policy_code = Column(String(50), nullable=False)
    name = Column(String(150), nullable=False)
    minimum_amount = Column(Numeric(18, 4), nullable=False, default=0)
    maximum_amount = Column(Numeric(18, 4), nullable=True)
    required_role = Column(String(80), nullable=False)
    approval_level = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=True)


class ApprovalRequest(Base):
    __tablename__ = "fc_approval_requests"
    __table_args__ = (Index("ix_fc_approval_tenant_status", "tenant_id", "status"),)
    request_number = Column(String(50), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    document_id = Column(String(36), nullable=False)
    requested_by_id = Column(String(36), nullable=False)
    amount = Column(Numeric(18, 4), nullable=False, default=0)
    policy_id = Column(String(36), ForeignKey("fc_approval_policies.id"), nullable=True)
    approval_level = Column(Integer, nullable=False, default=1)
    status = Column(String(20), nullable=False, default="PENDING")
    decided_by_id = Column(String(36), nullable=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    decision_note = Column(Text, nullable=True)


class CashForecastLine(Base):
    __tablename__ = "fc_cash_forecast_lines"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    forecast_type = Column(String(30), nullable=False)
    category = Column(String(80), nullable=False)
    description = Column(String(255), nullable=False)
    expected_amount = Column(Numeric(18, 4), nullable=False)
    probability_percent = Column(Numeric(5, 2), nullable=False, default=100)
    currency = Column(String(3), nullable=False, default="USD")
    source_type = Column(String(50), nullable=True)
    source_id = Column(String(36), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")


class ReconciliationException(Base):
    __tablename__ = "fc_reconciliation_exceptions"
    __table_args__ = (Index("ix_fc_recon_tenant_status", "tenant_id", "status"),)
    account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True)
    statement_reference = Column(String(100), nullable=False)
    transaction_date = Column(Date, nullable=False)
    book_amount = Column(Numeric(18, 4), nullable=False)
    statement_amount = Column(Numeric(18, 4), nullable=False)
    variance_amount = Column(Numeric(18, 4), nullable=False)
    exception_type = Column(String(40), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="OPEN")
    assigned_to_id = Column(String(36), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(String(36), nullable=True)
    resolution_note = Column(Text, nullable=True)
