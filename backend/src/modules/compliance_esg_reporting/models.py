"""
ESG & Carbon Emissions Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class FacilityEnergyEmissionLog(Base):
    """Energy consumption and calculated metric tons CO2e emission log."""
    __tablename__ = "esg_facility_emission_logs"

    facility_id = Column(String(36), nullable=False, index=True)
    facility_name = Column(String(150), nullable=False)
    reporting_period = Column(String(10), nullable=False)  # e.g. '2026-Q1'
    
    scope = Column(String(30), default="SCOPE_2_MARKET_BASED", nullable=False)
    energy_type = Column(String(50), nullable=False)  # ELECTRICITY_KWH, NATURAL_GAS_MMBTU, DIESEL_LITERS
    consumed_quantity = Column(Numeric(14, 4), nullable=False)
    unit_of_measure = Column(String(20), nullable=False)
    
    emission_factor_kg_co2e = Column(Numeric(10, 6), nullable=False)
    calculated_metric_tons_co2e = Column(Numeric(14, 4), nullable=False)
    is_verified_by_auditor = Column(Boolean, default=False, nullable=False)


class SupplierESGAudit(Base):
    """Supplier sustainability and CSRD supply chain scorecard."""
    __tablename__ = "esg_supplier_audits"

    vendor_id = Column(String(36), nullable=False, index=True)
    vendor_name = Column(String(150), nullable=False)
    audit_date = Column(Date, nullable=False)
    
    overall_esg_score = Column(Integer, default=70, nullable=False)  # 0 - 100
    environmental_score = Column(Integer, default=70, nullable=False)
    social_labor_score = Column(Integer, default=70, nullable=False)
    governance_ethics_score = Column(Integer, default=70, nullable=False)
    
    has_iso_14001_cert = Column(Boolean, default=False, nullable=False)
    has_sbti_commitment = Column(Boolean, default=False, nullable=False)
    audit_notes = Column(Text, nullable=True)
