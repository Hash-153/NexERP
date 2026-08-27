"""
Advanced Planning & Scheduling Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class ProductionWorkCenterResource(Base):
    """Shop floor machine / manufacturing work center capacity node."""
    __tablename__ = "aps_work_centers"

    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(150), nullable=False)
    plant_facility_id = Column(String(36), nullable=False, index=True)
    department = Column(String(80), nullable=False)
    
    daily_shift_hours = Column(Numeric(4, 2), default=16.0, nullable=False)
    number_of_machines = Column(Integer, default=1, nullable=False)
    hourly_standard_cost = Column(Numeric(10, 2), default=85.00, nullable=False)
    efficiency_factor_pct = Column(Numeric(5, 2), default=90.0, nullable=False)
    
    is_bottleneck_critical = Column(Boolean, default=False, nullable=False)
    is_operational = Column(Boolean, default=True, nullable=False)

    operations = relationship("ScheduledManufacturingOperation", back_populates="work_center")


class ScheduledManufacturingOperation(Base):
    """Gantt scheduled operation block with sequence prioritization."""
    __tablename__ = "aps_scheduled_operations"

    work_center_id = Column(String(36), ForeignKey("aps_work_centers.id"), nullable=False)
    work_order_number = Column(String(64), nullable=False, index=True)
    operation_sequence = Column(Integer, default=10, nullable=False)
    operation_name = Column(String(150), nullable=False)
    
    setup_hours = Column(Numeric(6, 2), default=0.5, nullable=False)
    run_hours = Column(Numeric(6, 2), default=4.0, nullable=False)
    total_planned_hours = Column(Numeric(6, 2), nullable=False)
    
    planned_start_time = Column(DateTime(timezone=True), nullable=False)
    planned_end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), default="SCHEDULED", nullable=False)  # SCHEDULED, RUNNING, COMPLETED, DELAYED

    work_center = relationship("ProductionWorkCenterResource", back_populates="operations")
