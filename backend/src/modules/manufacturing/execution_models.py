"""Manufacturing execution, quality, downtime, and scrap control models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from backend.src.core.database import Base


class OperatorSession(Base):
    __tablename__ = "mfg_operator_sessions"
    job_card_id = Column(String(36), ForeignKey("mfg_job_cards.id"), nullable=False)
    operator_id = Column(String(36), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    break_minutes = Column(Integer, nullable=False, default=0)
    productive_hours = Column(Numeric(8, 2), nullable=False, default=0)
    labor_cost = Column(Numeric(18, 4), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="OPEN")
    notes = Column(Text, nullable=True)


class ProductionQualityCheck(Base):
    __tablename__ = "mfg_production_quality_checks"
    __table_args__ = (Index("ix_mfg_quality_tenant_order", "tenant_id", "production_order_id"),)
    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id"), nullable=False)
    job_card_id = Column(String(36), ForeignKey("mfg_job_cards.id"), nullable=True)
    checkpoint_code = Column(String(50), nullable=False)
    checkpoint_name = Column(String(150), nullable=False)
    sample_size = Column(Numeric(14, 4), nullable=False, default=1)
    accepted_quantity = Column(Numeric(14, 4), nullable=False, default=0)
    rejected_quantity = Column(Numeric(14, 4), nullable=False, default=0)
    measurement_value = Column(Numeric(18, 6), nullable=True)
    lower_specification = Column(Numeric(18, 6), nullable=True)
    upper_specification = Column(Numeric(18, 6), nullable=True)
    inspector_id = Column(String(36), nullable=True)
    checked_at = Column(DateTime(timezone=True), nullable=False)
    result = Column(String(20), nullable=False, default="PENDING")
    notes = Column(Text, nullable=True)


class DowntimeEvent(Base):
    __tablename__ = "mfg_downtime_events"
    work_center_id = Column(String(36), ForeignKey("mfg_work_centers.id"), nullable=False)
    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id"), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=False, default=0)
    category = Column(String(40), nullable=False)
    reason_code = Column(String(50), nullable=False)
    reason_detail = Column(Text, nullable=True)
    planned = Column(Boolean, nullable=False, default=False)
    reported_by_id = Column(String(36), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")


class ScrapApproval(Base):
    __tablename__ = "mfg_scrap_approvals"
    __table_args__ = (Index("ix_mfg_scrap_tenant_status", "tenant_id", "status"),)
    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id"), nullable=False)
    job_card_id = Column(String(36), ForeignKey("mfg_job_cards.id"), nullable=True)
    quantity = Column(Numeric(14, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), nullable=False)
    total_cost = Column(Numeric(18, 4), nullable=False)
    reason_code = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=False)
    requested_by_id = Column(String(36), nullable=False)
    requested_at = Column(DateTime(timezone=True), nullable=False)
    approved_by_id = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    disposition = Column(String(40), nullable=True)


class ProductionKPI(Base):
    __tablename__ = "mfg_production_kpis"
    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id"), nullable=False)
    calculation_date = Column(Date, nullable=False)
    planned_quantity = Column(Numeric(14, 4), nullable=False)
    good_quantity = Column(Numeric(14, 4), nullable=False)
    scrap_quantity = Column(Numeric(14, 4), nullable=False)
    planned_hours = Column(Numeric(10, 2), nullable=False, default=0)
    actual_hours = Column(Numeric(10, 2), nullable=False, default=0)
    availability_percent = Column(Numeric(7, 2), nullable=False, default=0)
    performance_percent = Column(Numeric(7, 2), nullable=False, default=0)
    quality_percent = Column(Numeric(7, 2), nullable=False, default=0)
    oee_percent = Column(Numeric(7, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="FINAL")
