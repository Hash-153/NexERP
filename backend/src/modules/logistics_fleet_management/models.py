"""
Logistics & Fleet Management Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class FreightCarrier(Base):
    """Third-party logistics carrier or private corporate fleet."""
    __tablename__ = "log_carriers"

    carrier_code = Column(String(30), nullable=False, unique=True, index=True)
    company_name = Column(String(150), nullable=False)
    scac_code = Column(String(10), nullable=True, doc="Standard Carrier Alpha Code")
    dot_number = Column(String(20), nullable=True)
    transport_mode = Column(String(30), default="ROAD_FTL", nullable=False)
    contact_email = Column(String(100), nullable=False)
    contact_phone = Column(String(30), nullable=True)
    is_preferred = Column(Boolean, default=False, nullable=False)
    performance_rating = Column(Numeric(3, 2), default=4.5, nullable=False)

    dispatches = relationship("ShipmentDispatch", back_populates="carrier")


class ShipmentDispatch(Base):
    """Multi-modal consignment shipment dispatch record."""
    __tablename__ = "log_shipment_dispatches"

    carrier_id = Column(String(36), ForeignKey("log_carriers.id"), nullable=False)
    tracking_bol_number = Column(String(64), nullable=False, unique=True, index=True)
    transport_mode = Column(String(30), default="ROAD_FTL", nullable=False)
    status = Column(String(30), default="BOOKED", nullable=False)
    
    origin_address = Column(String(255), nullable=False)
    destination_address = Column(String(255), nullable=False)
    scheduled_pickup = Column(DateTime(timezone=True), nullable=False)
    estimated_delivery = Column(DateTime(timezone=True), nullable=False)
    actual_delivery = Column(DateTime(timezone=True), nullable=True)
    
    total_pallets = Column(Integer, default=1, nullable=False)
    gross_weight_kg = Column(Numeric(12, 2), nullable=False)
    dimensional_weight_kg = Column(Numeric(12, 2), nullable=False)
    chargeable_weight_kg = Column(Numeric(12, 2), nullable=False)
    
    quoted_freight_charge = Column(Numeric(14, 4), nullable=False)
    fuel_surcharge = Column(Numeric(14, 4), default=0.0, nullable=False)
    accessorial_charges = Column(Numeric(14, 4), default=0.0, nullable=False)
    total_cost = Column(Numeric(14, 4), nullable=False)

    carrier = relationship("FreightCarrier", back_populates="dispatches")
    telematics = relationship("FleetTelematicsPing", back_populates="shipment", cascade="all, delete-orphan")


class FleetTelematicsPing(Base):
    """Live GPS, speed, and environmental sensor telemetry breadcrumb."""
    __tablename__ = "log_telematics_pings"

    shipment_id = Column(String(36), ForeignKey("log_shipment_dispatches.id", ondelete="CASCADE"), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    speed_kmh = Column(Numeric(5, 2), default=0.0, nullable=False)
    temperature_c = Column(Numeric(5, 2), nullable=True)
    geofence_status = Column(String(30), default="INSIDE_CORRIDOR", nullable=False)

    shipment = relationship("ShipmentDispatch", back_populates="telematics")
