"""Advanced CRM pipeline, activities, forecasts, and follow-up models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class PipelineStage(Base):
    __tablename__ = "sales_pipeline_stages"
    code = Column(String(40), nullable=False)
    name = Column(String(100), nullable=False)
    sequence = Column(Integer, nullable=False, default=1)
    probability_percent = Column(Integer, nullable=False, default=20)
    is_closed = Column(Boolean, nullable=False, default=False)
    is_won = Column(Boolean, nullable=False, default=False)
    color = Column(String(20), nullable=False, default="blue")


class Opportunity(Base):
    __tablename__ = "sales_opportunities"
    __table_args__ = (Index("ix_sales_opportunity_tenant_stage", "tenant_id", "stage_code"),)
    opportunity_number = Column(String(50), nullable=False, index=True)
    lead_id = Column(String(36), ForeignKey("sales_leads.id"), nullable=True)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    name = Column(String(200), nullable=False)
    stage_code = Column(String(40), nullable=False, default="QUALIFICATION")
    amount = Column(Numeric(18, 4), nullable=False, default=0)
    probability_percent = Column(Integer, nullable=False, default=20)
    expected_close_date = Column(Date, nullable=True)
    source = Column(String(100), nullable=True)
    owner_id = Column(String(36), nullable=True)
    competitor = Column(String(150), nullable=True)
    next_step = Column(String(255), nullable=True)
    last_contact_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")
    loss_reason = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    activities = relationship("CRMActivity", back_populates="opportunity", cascade="all, delete-orphan")


class CRMActivity(Base):
    __tablename__ = "sales_crm_activities"
    opportunity_id = Column(String(36), ForeignKey("sales_opportunities.id", ondelete="CASCADE"), nullable=True)
    lead_id = Column(String(36), ForeignKey("sales_leads.id"), nullable=True)
    activity_type = Column(String(30), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    owner_id = Column(String(36), nullable=True)
    outcome = Column(String(255), nullable=True)
    opportunity = relationship("Opportunity", back_populates="activities")


class ForecastSnapshot(Base):
    __tablename__ = "sales_forecast_snapshots"
    snapshot_date = Column(Date, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    owner_id = Column(String(36), nullable=True)
    pipeline_amount = Column(Numeric(18, 4), nullable=False, default=0)
    weighted_amount = Column(Numeric(18, 4), nullable=False, default=0)
    committed_amount = Column(Numeric(18, 4), nullable=False, default=0)
    best_case_amount = Column(Numeric(18, 4), nullable=False, default=0)
    opportunity_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="DRAFT")


class CRMTask(Base):
    __tablename__ = "sales_crm_tasks"
    opportunity_id = Column(String(36), ForeignKey("sales_opportunities.id"), nullable=True)
    lead_id = Column(String(36), ForeignKey("sales_leads.id"), nullable=True)
    title = Column(String(200), nullable=False)
    due_date = Column(Date, nullable=False)
    priority = Column(String(20), nullable=False, default="NORMAL")
    assigned_to_id = Column(String(36), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
