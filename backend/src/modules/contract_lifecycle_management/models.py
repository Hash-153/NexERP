"""
Contract Lifecycle Management Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class ContractDocument(Base):
    """Core enterprise legal contract repository record."""
    __tablename__ = "clm_contract_documents"

    contract_number = Column(String(64), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    contract_type = Column(String(50), default="MASTER_SERVICES_AGREEMENT", nullable=False)
    status = Column(String(40), default="DRAFT_AUTHORING", nullable=False)
    
    counterparty_name = Column(String(150), nullable=False)
    counterparty_signatory_email = Column(String(150), nullable=False)
    internal_owner_user_id = Column(String(36), nullable=False)
    
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    renewal_type = Column(String(40), default="EVERGREEN_AUTO_RENEW", nullable=False)
    renewal_notice_days = Column(Integer, default=60, nullable=False)
    
    total_contract_value = Column(Numeric(14, 4), default=0.0, nullable=False)
    governing_law_jurisdiction = Column(String(100), default="Delaware, USA", nullable=False)
    cpi_escalation_pct = Column(Numeric(5, 2), default=3.0, nullable=False)
    
    digital_envelope_id = Column(String(100), nullable=True)
    fully_executed_pdf_url = Column(String(255), nullable=True)

    milestones = relationship("ContractMilestoneBilling", back_populates="contract", cascade="all, delete-orphan")


class ContractMilestoneBilling(Base):
    """Milestone-based revenue recognition and billing schedule."""
    __tablename__ = "clm_milestone_billings"

    contract_id = Column(String(36), ForeignKey("clm_contract_documents.id", ondelete="CASCADE"), nullable=False)
    milestone_name = Column(String(150), nullable=False)
    milestone_percentage = Column(Numeric(5, 2), nullable=False)
    billing_amount = Column(Numeric(14, 4), nullable=False)
    target_delivery_date = Column(Date, nullable=False)
    is_deliverable_accepted = Column(Boolean, default=False, nullable=False)
    accepted_by_user_id = Column(String(36), nullable=True)
    invoice_id = Column(String(36), nullable=True)

    contract = relationship("ContractDocument", back_populates="milestones")
