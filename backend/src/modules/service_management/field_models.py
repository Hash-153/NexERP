"""Field service execution, preventive maintenance, knowledge, and feedback models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class ServiceTechnician(Base):
    """Technician profile with skills, territory, and utilization targets."""
    __tablename__ = "sm_technicians"
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    technician_code = Column(String(40), nullable=False, index=True)
    display_name = Column(String(150), nullable=False)
    territory = Column(String(100), nullable=True)
    skill_group = Column(String(100), nullable=True)
    phone = Column(String(40), nullable=True)
    hourly_cost = Column(Numeric(18, 4), nullable=False, default=0)
    hourly_rate = Column(Numeric(18, 4), nullable=False, default=0)
    utilization_target = Column(Numeric(5, 2), nullable=False, default=75)
    status = Column(String(20), nullable=False, default="AVAILABLE")
    dispatches = relationship("DispatchOrder", back_populates="technician")


class DispatchOrder(Base):
    """Planned or active technician visit for a ticket."""
    __tablename__ = "sm_dispatch_orders"
    __table_args__ = (Index("ix_sm_dispatch_tenant_schedule", "tenant_id", "scheduled_start"),)
    dispatch_number = Column(String(50), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    technician_id = Column(String(36), ForeignKey("sm_technicians.id"), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_start = Column(DateTime(timezone=True), nullable=True)
    actual_end = Column(DateTime(timezone=True), nullable=True)
    address = Column(String(255), nullable=True)
    visit_type = Column(String(30), nullable=False, default="ON_SITE")
    status = Column(String(30), nullable=False, default="PLANNED")
    travel_minutes = Column(Integer, nullable=False, default=0)
    arrival_notes = Column(Text, nullable=True)
    completion_notes = Column(Text, nullable=True)
    technician = relationship("ServiceTechnician", back_populates="dispatches")


class MaintenancePlan(Base):
    """Recurring preventive maintenance policy for a customer asset."""
    __tablename__ = "sm_maintenance_plans"
    plan_number = Column(String(50), nullable=False, index=True)
    asset_id = Column(String(36), ForeignKey("sm_customer_assets.id"), nullable=False)
    name = Column(String(200), nullable=False)
    frequency_days = Column(Integer, nullable=False)
    next_due_date = Column(Date, nullable=False)
    last_completed_date = Column(Date, nullable=True)
    estimated_hours = Column(Numeric(8, 2), nullable=False, default=1)
    checklist = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")


class KnowledgeArticle(Base):
    """Searchable resolution guidance for agents and customers."""
    __tablename__ = "sm_knowledge_articles"
    article_number = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(80), nullable=False, default="GENERAL")
    audience = Column(String(20), nullable=False, default="INTERNAL")
    version = Column(Integer, nullable=False, default=1)
    published_at = Column(DateTime(timezone=True), nullable=True)
    view_count = Column(Integer, nullable=False, default=0)
    helpful_count = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="DRAFT")


class CustomerFeedback(Base):
    """Post-resolution customer satisfaction response."""
    __tablename__ = "sm_customer_feedback"
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    rating = Column(Integer, nullable=False)
    response_time_rating = Column(Integer, nullable=True)
    resolution_rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=False)
    is_public = Column(Boolean, nullable=False, default=False)
