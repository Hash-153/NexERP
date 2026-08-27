"""
CRM & CPQ Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class CRMLead(Base):
    """Prospective business lead with predictive qualification scoring."""
    __tablename__ = "crm_leads"

    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), nullable=False, index=True)
    company_name = Column(String(150), nullable=False)
    job_title = Column(String(100), nullable=True)
    lead_source = Column(String(40), default="ORGANIC_WEB", nullable=False)
    qualification_status = Column(String(40), default="NEW_UNTOUCHED", nullable=False)
    
    predictive_score = Column(Integer, default=50, nullable=False)  # 0 - 100
    budget_amount = Column(Numeric(14, 4), nullable=True)
    decision_timeframe_months = Column(Integer, default=3, nullable=False)
    
    assigned_sales_rep_id = Column(String(36), nullable=True)
    converted_opportunity_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)

    activities = relationship("CRMLeadActivity", back_populates="lead", cascade="all, delete-orphan")


class CRMLeadActivity(Base):
    """Touchpoint history log (Calls, Emails, Demos, Site Visits)."""
    __tablename__ = "crm_lead_activities"

    lead_id = Column(String(36), ForeignKey("crm_leads.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(30), nullable=False)  # EMAIL, CALL, MEETING, DEMO, NOTE
    subject = Column(String(200), nullable=False)
    performed_at = Column(DateTime(timezone=True), nullable=False)
    performed_by_user_id = Column(String(36), nullable=False)
    outcome_sentiment = Column(String(20), default="NEUTRAL", nullable=False)  # POSITIVE, NEUTRAL, NEGATIVE
    notes = Column(Text, nullable=True)

    lead = relationship("CRMLead", back_populates="activities")


class CRMOpportunity(Base):
    """Sales Opportunity pipeline deal container."""
    __tablename__ = "crm_opportunities"

    opportunity_name = Column(String(200), nullable=False)
    account_id = Column(String(36), nullable=False, index=True)
    primary_contact_id = Column(String(36), nullable=True)
    stage = Column(String(40), default="PROSPECTING", nullable=False)
    deal_value = Column(Numeric(14, 4), default=0.0, nullable=False)
    weighted_pipeline_value = Column(Numeric(14, 4), default=0.0, nullable=False)
    win_probability_pct = Column(Integer, default=20, nullable=False)
    expected_close_date = Column(Date, nullable=False)
    
    assigned_sales_rep_id = Column(String(36), nullable=False)
    lead_source = Column(String(40), default="ORGANIC_WEB", nullable=False)
    loss_reason = Column(String(255), nullable=True)

    quotes = relationship("CPQQuote", back_populates="opportunity", cascade="all, delete-orphan")


class CPQQuote(Base):
    """Configure, Price, Quote (CPQ) commercial quotation proposal."""
    __tablename__ = "crm_cpq_quotes"

    opportunity_id = Column(String(36), ForeignKey("crm_opportunities.id", ondelete="CASCADE"), nullable=False)
    quote_number = Column(String(64), nullable=False, unique=True, index=True)
    version = Column(Integer, default=1, nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False)  # DRAFT, IN_REVIEW, APPROVED, PRESENTED, ACCEPTED, REJECTED
    
    gross_total = Column(Numeric(14, 4), default=0.0, nullable=False)
    discount_total = Column(Numeric(14, 4), default=0.0, nullable=False)
    tax_total = Column(Numeric(14, 4), default=0.0, nullable=False)
    net_total = Column(Numeric(14, 4), default=0.0, nullable=False)
    margin_percentage = Column(Numeric(5, 2), default=35.0, nullable=False)
    
    is_primary_quote = Column(Boolean, default=True, nullable=False)
    valid_until_date = Column(Date, nullable=False)

    opportunity = relationship("CRMOpportunity", back_populates="quotes")
    lines = relationship("CPQQuoteLine", back_populates="quote", cascade="all, delete-orphan")


class CPQQuoteLine(Base):
    """Configured SKU line item with pricing rule modifiers."""
    __tablename__ = "crm_cpq_quote_lines"

    quote_id = Column(String(36), ForeignKey("crm_cpq_quotes.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Numeric(14, 4), default=1.0, nullable=False)
    list_unit_price = Column(Numeric(14, 4), nullable=False)
    unit_cost = Column(Numeric(14, 4), default=0.0, nullable=False)
    discount_percentage = Column(Numeric(5, 2), default=0.0, nullable=False)
    net_unit_price = Column(Numeric(14, 4), nullable=False)
    extended_price = Column(Numeric(14, 4), nullable=False)

    quote = relationship("CPQQuote", back_populates="lines")
