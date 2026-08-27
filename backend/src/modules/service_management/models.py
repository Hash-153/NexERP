"""Service contracts, customer equipment, tickets, SLAs, and field execution models."""

from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class ServiceContract(Base):
    __tablename__ = "sm_service_contracts"
    contract_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    name = Column(String(200), nullable=False)
    contract_type = Column(String(30), nullable=False, default="TIME_AND_MATERIALS")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    currency = Column(String(3), nullable=False, default="USD")
    value = Column(Numeric(18, 4), nullable=False, default=0)
    response_hours = Column(Numeric(8, 2), nullable=False, default=24)
    resolution_hours = Column(Numeric(8, 2), nullable=False, default=72)
    included_hours = Column(Numeric(10, 2), nullable=False, default=0)
    consumed_hours = Column(Numeric(10, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="DRAFT")
    notes = Column(Text, nullable=True)
    tickets = relationship("ServiceTicket", back_populates="contract")


class CustomerAsset(Base):
    __tablename__ = "sm_customer_assets"
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    asset_number = Column(String(50), nullable=False, index=True)
    serial_number = Column(String(100), nullable=True, index=True)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=True)
    name = Column(String(200), nullable=False)
    model = Column(String(100), nullable=True)
    installed_on = Column(Date, nullable=True)
    warranty_end_date = Column(Date, nullable=True)
    location = Column(String(200), nullable=True)
    meter_value = Column(Numeric(14, 2), nullable=False, default=0)
    meter_unit = Column(String(30), nullable=False, default="HOURS")
    status = Column(String(20), nullable=False, default="ACTIVE")
    tickets = relationship("ServiceTicket", back_populates="asset")


class ServiceTicket(Base):
    __tablename__ = "sm_service_tickets"
    __table_args__ = (Index("ix_sm_ticket_tenant_status", "tenant_id", "status"),)
    ticket_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    contract_id = Column(String(36), ForeignKey("sm_service_contracts.id"), nullable=True)
    asset_id = Column(String(36), ForeignKey("sm_customer_assets.id"), nullable=True)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    channel = Column(String(20), nullable=False, default="PORTAL")
    priority = Column(String(20), nullable=False, default="NORMAL")
    status = Column(String(30), nullable=False, default="OPEN")
    assigned_to_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=False)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    billable = Column(Boolean, nullable=False, default=True)
    estimated_hours = Column(Numeric(8, 2), nullable=False, default=0)
    actual_hours = Column(Numeric(8, 2), nullable=False, default=0)
    resolution_notes = Column(Text, nullable=True)
    contract = relationship("ServiceContract", back_populates="tickets")
    asset = relationship("CustomerAsset", back_populates="tickets")
    activities = relationship("ServiceActivity", back_populates="ticket", cascade="all, delete-orphan")


class ServiceActivity(Base):
    __tablename__ = "sm_service_activities"
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id", ondelete="CASCADE"), nullable=False)
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    activity_type = Column(String(30), nullable=False, default="WORK")
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    hours = Column(Numeric(8, 2), nullable=False, default=0)
    hourly_rate = Column(Numeric(18, 4), nullable=False, default=0)
    description = Column(Text, nullable=False)
    billable = Column(Boolean, nullable=False, default=True)
    ticket = relationship("ServiceTicket", back_populates="activities")


class ServicePartUsage(Base):
    __tablename__ = "sm_service_part_usage"
    ticket_id = Column(String(36), ForeignKey("sm_service_tickets.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    quantity = Column(Numeric(14, 4), nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False, default=0)
    cost = Column(Numeric(18, 4), nullable=False, default=0)
    billable = Column(Boolean, nullable=False, default=True)
    description = Column(String(255), nullable=True)
