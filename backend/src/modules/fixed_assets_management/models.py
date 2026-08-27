"""
Fixed Assets Management Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class FixedAssetMaster(Base):
    """Core master record for physical or intangible capitalized assets."""
    __tablename__ = "fa_asset_masters"

    asset_tag = Column(String(50), nullable=False, unique=True, index=True)
    serial_number = Column(String(100), nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, index=True)
    status = Column(String(40), default="ACTIVE_IN_SERVICE", nullable=False)
    
    acquisition_date = Column(Date, nullable=False)
    in_service_date = Column(Date, nullable=False)
    original_acquisition_cost = Column(Numeric(18, 4), nullable=False)
    salvage_scrap_value = Column(Numeric(18, 4), default=0.0, nullable=False)
    useful_life_months = Column(Integer, nullable=False)
    
    current_net_book_value = Column(Numeric(18, 4), nullable=False)
    accumulated_depreciation = Column(Numeric(18, 4), default=0.0, nullable=False)
    accumulated_impairment = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    location_facility = Column(String(100), nullable=True)
    cost_center_code = Column(String(50), nullable=True)
    custodian_employee_id = Column(String(36), nullable=True)
    
    gl_asset_account_id = Column(String(36), nullable=True)
    gl_depreciation_account_id = Column(String(36), nullable=True)
    gl_expense_account_id = Column(String(36), nullable=True)

    schedules = relationship("AssetDepreciationSchedule", back_populates="asset", cascade="all, delete-orphan")
    audits = relationship("AssetPhysicalAudit", back_populates="asset")


class AssetDepreciationSchedule(Base):
    """Calculated monthly depreciation schedules across financial / tax books."""
    __tablename__ = "fa_depreciation_schedules"

    asset_id = Column(String(36), ForeignKey("fa_asset_masters.id", ondelete="CASCADE"), nullable=False)
    fiscal_period = Column(String(10), nullable=False)  # e.g. '2026-03'
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    depreciation_method = Column(String(40), default="STRAIGHT_LINE", nullable=False)
    book_type = Column(String(30), default="CORPORATE_GAAP", nullable=False)  # CORPORATE_GAAP, FEDERAL_TAX, IFRS
    
    opening_carrying_value = Column(Numeric(18, 4), nullable=False)
    depreciation_amount = Column(Numeric(18, 4), nullable=False)
    closing_carrying_value = Column(Numeric(18, 4), nullable=False)
    
    is_posted_to_gl = Column(Boolean, default=False, nullable=False)
    gl_journal_entry_id = Column(String(36), nullable=True)

    asset = relationship("FixedAssetMaster", back_populates="schedules")


class AssetPhysicalAudit(Base):
    """Barcode/RFID physical inspection scan record."""
    __tablename__ = "fa_physical_audits"

    asset_id = Column(String(36), ForeignKey("fa_asset_masters.id"), nullable=False)
    audit_batch_code = Column(String(64), nullable=False, index=True)
    scanned_at = Column(DateTime(timezone=True), nullable=False)
    scanned_by_user_id = Column(String(36), nullable=False)
    detected_location = Column(String(100), nullable=False)
    condition_rating = Column(String(30), default="GOOD", nullable=False)  # EXCELLENT, GOOD, FAIR, POOR, DAMAGED
    is_location_discrepancy = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    asset = relationship("FixedAssetMaster", back_populates="audits")
