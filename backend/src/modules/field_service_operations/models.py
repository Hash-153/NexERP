"""
Field Service Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class ServiceTechnician(Base):
    """Field service engineer / certified technician profile."""
    __tablename__ = "fso_technicians"

    user_id = Column(String(36), nullable=False, unique=True, index=True)
    employee_code = Column(String(50), nullable=False)
    full_name = Column(String(150), nullable=False)
    primary_phone = Column(String(30), nullable=False)
    home_base_location = Column(String(150), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    active_skills_list = Column(JSON, nullable=True)  # ["HVAC_LV3", "PLC_SIEMENS", "ELECTRICAL_CERT"]

    work_orders = relationship("FieldWorkOrder", back_populates="technician")


class FieldWorkOrder(Base):
    """On-site field service dispatch job."""
    __tablename__ = "fso_work_orders"

    order_number = Column(String(64), nullable=False, unique=True, index=True)
    customer_account_id = Column(String(36), nullable=False, index=True)
    site_location_address = Column(String(255), nullable=False)
    asset_serial_number = Column(String(100), nullable=True)
    
    priority = Column(String(30), default="MEDIUM", nullable=False)
    status = Column(String(40), default="UNASSIGNED", nullable=False)
    sla_severity = Column(String(40), default="P2_NEXT_BUSINESS_DAY", nullable=False)
    
    technician_id = Column(String(36), ForeignKey("fso_technicians.id"), nullable=True)
    scheduled_start = Column(DateTime(timezone=True), nullable=False)
    scheduled_end = Column(DateTime(timezone=True), nullable=False)
    actual_arrival_time = Column(DateTime(timezone=True), nullable=True)
    actual_completion_time = Column(DateTime(timezone=True), nullable=True)
    
    issue_description = Column(Text, nullable=False)
    resolution_summary = Column(Text, nullable=True)
    customer_signature_token = Column(String(255), nullable=True)
    customer_rating = Column(Integer, nullable=True)

    technician = relationship("ServiceTechnician", back_populates="work_orders")
    consumed_parts = relationship("WorkOrderPartUsage", back_populates="work_order", cascade="all, delete-orphan")


class WorkOrderPartUsage(Base):
    """Inventory spare parts debited from mobile van stock."""
    __tablename__ = "fso_part_usages"

    work_order_id = Column(String(36), ForeignKey("fso_work_orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), nullable=False)
    part_number = Column(String(100), nullable=False)
    part_name = Column(String(150), nullable=False)
    quantity_used = Column(Numeric(10, 2), default=1.0, nullable=False)
    unit_cost = Column(Numeric(14, 4), nullable=False)
    is_warranty_covered = Column(Boolean, default=False, nullable=False)

    work_order = relationship("FieldWorkOrder", back_populates="consumed_parts")
