"""
Advanced WMS Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class WarehouseZone(Base):
    """Logical and environmental storage zone in a distribution center."""
    __tablename__ = "wms_zones"

    warehouse_id = Column(String(36), nullable=False, index=True)
    zone_code = Column(String(20), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    zone_type = Column(String(40), default="HIGH_BAY_RACK", nullable=False)
    temperature_min_c = Column(Numeric(5, 2), nullable=True)
    temperature_max_c = Column(Numeric(5, 2), nullable=True)
    is_bonded = Column(Boolean, default=False, nullable=False)
    is_hazardous = Column(Boolean, default=False, nullable=False)

    locations = relationship("WarehouseLocation", back_populates="zone", cascade="all, delete-orphan")


class WarehouseLocation(Base):
    """Specific 3D coordinate bin/rack location (Aisle-Bay-Shelf-Bin)."""
    __tablename__ = "wms_locations"

    zone_id = Column(String(36), ForeignKey("wms_zones.id", ondelete="CASCADE"), nullable=False)
    location_barcode = Column(String(50), nullable=False, unique=True, index=True)
    aisle = Column(String(10), nullable=False)
    bay = Column(String(10), nullable=False)
    shelf = Column(String(10), nullable=False)
    bin = Column(String(10), nullable=False)
    
    max_weight_kg = Column(Numeric(10, 2), default=1000.0, nullable=False)
    current_weight_kg = Column(Numeric(10, 2), default=0.0, nullable=False)
    max_volume_cbm = Column(Numeric(10, 4), default=2.5, nullable=False)
    occupied_volume_cbm = Column(Numeric(10, 4), default=0.0, nullable=False)
    
    velocity_class = Column(String(5), default="B", nullable=False)  # A (Fast), B (Medium), C (Slow)
    is_blocked = Column(Boolean, default=False, nullable=False)
    is_pick_face = Column(Boolean, default=True, nullable=False)

    zone = relationship("WarehouseZone", back_populates="locations")


class WaveBatchRun(Base):
    """Grouped wave picking execution batch."""
    __tablename__ = "wms_wave_batches"

    wave_number = Column(String(50), nullable=False, unique=True, index=True)
    carrier_cutoff_time = Column(DateTime(timezone=True), nullable=True)
    priority_level = Column(Integer, default=5, nullable=False)
    status = Column(String(30), default="RELEASED", nullable=False)  # RELEASED, IN_PROGRESS, COMPLETED, CANCELLED
    total_lines = Column(Integer, default=0, nullable=False)
    picked_lines = Column(Integer, default=0, nullable=False)
    assigned_picker_id = Column(String(36), nullable=True)

    tasks = relationship("WavePickTask", back_populates="wave", cascade="all, delete-orphan")


class WavePickTask(Base):
    """Directed task assigned to picker RF gun."""
    __tablename__ = "wms_pick_tasks"

    wave_id = Column(String(36), ForeignKey("wms_wave_batches.id", ondelete="CASCADE"), nullable=False)
    sales_order_id = Column(String(36), nullable=False, index=True)
    item_id = Column(String(36), nullable=False, index=True)
    location_id = Column(String(36), ForeignKey("wms_locations.id"), nullable=False)
    
    requested_qty = Column(Numeric(14, 4), nullable=False)
    picked_qty = Column(Numeric(14, 4), default=0.0, nullable=False)
    sequence_order = Column(Integer, default=1, nullable=False)
    status = Column(String(30), default="PENDING", nullable=False)
    scanned_barcode = Column(String(100), nullable=True)
    tote_license_plate = Column(String(50), nullable=True)

    wave = relationship("WaveBatchRun", back_populates="tasks")


class YardDockDoor(Base):
    """Trailer parking and dock scheduling slot."""
    __tablename__ = "wms_dock_doors"

    door_number = Column(String(20), nullable=False, unique=True, index=True)
    door_type = Column(String(30), default="CROSS_DOCK", nullable=False)  # INBOUND, OUTBOUND, CROSS_DOCK
    status = Column(String(30), default="AVAILABLE", nullable=False)
    current_trailer_plate = Column(String(50), nullable=True)
    current_carrier_name = Column(String(100), nullable=True)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_departure = Column(DateTime(timezone=True), nullable=True)
