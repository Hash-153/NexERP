"""Invoice-ready service charges and SLA escalation records."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Numeric, String, Text
from backend.src.core.database import Base


class ServiceCharge(Base):
    """Billable time, travel, or material charge attached to a service ticket."""
    __tablename__ = "sm_service_charges"
    __table_args__ = (Index("ix_sm_charge_tenant_status", "tenant_id", "status"),)
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    contract_id = Column(String(36), ForeignKey("sm_service_contracts.id"), nullable=True)
    charge_date = Column(Date, nullable=False)
    charge_type = Column(String(30), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(14, 4), nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(5, 2), nullable=False, default=0)
    tax_percent = Column(Numeric(5, 2), nullable=False, default=0)
    net_amount = Column(Numeric(18, 4), nullable=False)
    tax_amount = Column(Numeric(18, 4), nullable=False, default=0)
    total_amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    status = Column(String(20), nullable=False, default="DRAFT")
    invoice_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)


class ServiceInvoiceBatch(Base):
    """Grouping of approved charges for downstream AR invoice creation."""
    __tablename__ = "sm_invoice_batches"
    batch_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(36), nullable=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    charge_count = Column(Numeric(10, 0), nullable=False, default=0)
    net_amount = Column(Numeric(18, 4), nullable=False, default=0)
    tax_amount = Column(Numeric(18, 4), nullable=False, default=0)
    total_amount = Column(Numeric(18, 4), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="DRAFT")
    posted_at = Column(DateTime(timezone=True), nullable=True)
    posted_by_id = Column(String(36), nullable=True)


class SLAEscalation(Base):
    """Auditable escalation raised when a ticket approaches or breaches an SLA."""
    __tablename__ = "sm_sla_escalations"
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    contract_id = Column(String(36), ForeignKey("sm_service_contracts.id"), nullable=True)
    escalation_level = Column(String(20), nullable=False)
    trigger = Column(String(30), nullable=False)
    threshold_percent = Column(Numeric(5, 2), nullable=False)
    detected_at = Column(DateTime(timezone=True), nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by_id = Column(String(36), nullable=True)
    owner_id = Column(String(36), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")
    notes = Column(Text, nullable=True)
