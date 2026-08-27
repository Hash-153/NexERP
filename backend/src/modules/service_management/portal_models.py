"""Customer portal conversations, appointment requests, and access tokens."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from backend.src.core.database import Base


class PortalAccessToken(Base):
    """Revocable, tenant-scoped token record for customer portal sessions."""
    __tablename__ = "sm_portal_access_tokens"
    __table_args__ = (Index("ix_sm_portal_token_hash", "token_hash", unique=True),)
    customer_id = Column(String(36), nullable=False)
    token_hash = Column(String(128), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    label = Column(String(100), nullable=True)


class PortalConversation(Base):
    """A customer-visible message linked to a service ticket."""
    __tablename__ = "sm_portal_conversations"
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    customer_id = Column(String(36), nullable=False)
    author_type = Column(String(20), nullable=False)
    author_id = Column(String(36), nullable=True)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=False)
    is_internal = Column(Boolean, nullable=False, default=False)
    attachment_count = Column(String(10), nullable=False, default="0")


class AppointmentRequest(Base):
    """Customer-requested visit window awaiting dispatcher confirmation."""
    __tablename__ = "sm_appointment_requests"
    __table_args__ = (Index("ix_sm_appointment_tenant_status", "tenant_id", "status"),)
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    customer_id = Column(String(36), nullable=False)
    preferred_start = Column(DateTime(timezone=True), nullable=False)
    preferred_end = Column(DateTime(timezone=True), nullable=False)
    alternate_start = Column(DateTime(timezone=True), nullable=True)
    alternate_end = Column(DateTime(timezone=True), nullable=True)
    timezone_name = Column(String(60), nullable=False, default="UTC")
    contact_name = Column(String(150), nullable=False)
    contact_phone = Column(String(40), nullable=True)
    access_instructions = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="REQUESTED")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by_id = Column(String(36), nullable=True)
    review_notes = Column(Text, nullable=True)
