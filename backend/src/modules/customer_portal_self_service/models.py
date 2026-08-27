"""
Customer Self-Service Portal Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class CustomerSupportTicket(Base):
    """Customer-initiated technical support / service ticket."""
    __tablename__ = "cp_support_tickets"

    ticket_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_account_id = Column(String(36), nullable=False, index=True)
    contact_email = Column(String(150), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(40), default="SEV_3_MEDIUM_INQUIRY", nullable=False)
    status = Column(String(30), default="OPEN", nullable=False)  # OPEN, IN_TRIAGE, WAITING_CUSTOMER, RESOLVED, CLOSED
    assigned_agent_id = Column(String(36), nullable=True)


class CustomerRMARequest(Base):
    """Return Merchandise Authorization (RMA) tracking."""
    __tablename__ = "cp_rma_requests"

    rma_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_account_id = Column(String(36), nullable=False, index=True)
    original_sales_order_id = Column(String(36), nullable=False, index=True)
    item_id = Column(String(36), nullable=False)
    quantity_to_return = Column(Numeric(10, 2), nullable=False)
    return_reason = Column(String(100), nullable=False)
    status = Column(String(40), default="REQUESTED", nullable=False)
    restocking_fee_pct = Column(Numeric(5, 2), default=0.0, nullable=False)
    prepaid_return_tracking_number = Column(String(100), nullable=True)
