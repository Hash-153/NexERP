"""Persistent supply planning and supplier performance models."""

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class DemandForecast(Base):
    __tablename__ = "sp_demand_forecasts"
    __table_args__ = (Index("ix_sp_forecast_tenant_item_period", "tenant_id", "item_id", "period_start"),)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    forecast_quantity = Column(Numeric(18, 4), nullable=False)
    baseline_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    promotion_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    confidence_percent = Column(Numeric(5, 2), nullable=False, default=50)
    method = Column(String(40), nullable=False, default="MOVING_AVERAGE")
    actual_quantity = Column(Numeric(18, 4), nullable=True)
    status = Column(String(20), nullable=False, default="OPEN")


class ReplenishmentPolicy(Base):
    __tablename__ = "sp_replenishment_policies"
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    planning_method = Column(String(30), nullable=False, default="MIN_MAX")
    review_period_days = Column(Integer, nullable=False, default=7)
    lead_time_days = Column(Integer, nullable=False, default=7)
    safety_stock_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    reorder_point_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    minimum_order_quantity = Column(Numeric(18, 4), nullable=False, default=1)
    maximum_order_quantity = Column(Numeric(18, 4), nullable=True)
    order_multiple = Column(Numeric(18, 4), nullable=False, default=1)
    preferred_supplier_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=True)
    active = Column(Boolean, nullable=False, default=True)


class PurchaseRecommendation(Base):
    __tablename__ = "sp_purchase_recommendations"
    recommendation_number = Column(String(50), nullable=False, index=True)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    supplier_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=True)
    required_date = Column(Date, nullable=False)
    demand_quantity = Column(Numeric(18, 4), nullable=False)
    available_quantity = Column(Numeric(18, 4), nullable=False)
    safety_stock_quantity = Column(Numeric(18, 4), nullable=False)
    recommended_quantity = Column(Numeric(18, 4), nullable=False)
    estimated_unit_cost = Column(Numeric(18, 4), nullable=False, default=0)
    estimated_total_cost = Column(Numeric(18, 4), nullable=False, default=0)
    reason = Column(String(100), nullable=False)
    priority = Column(String(20), nullable=False, default="NORMAL")
    status = Column(String(20), nullable=False, default="PROPOSED")
    approved_by_id = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)


class SupplierScorecard(Base):
    __tablename__ = "sp_supplier_scorecards"
    supplier_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    order_count = Column(Integer, nullable=False, default=0)
    on_time_count = Column(Integer, nullable=False, default=0)
    received_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    accepted_quantity = Column(Numeric(18, 4), nullable=False, default=0)
    spend_amount = Column(Numeric(18, 4), nullable=False, default=0)
    on_time_percent = Column(Numeric(5, 2), nullable=False, default=0)
    quality_percent = Column(Numeric(5, 2), nullable=False, default=0)
    composite_score = Column(Numeric(5, 2), nullable=False, default=0)
    status = Column(String(20), nullable=False, default="DRAFT")


class ShipmentMilestone(Base):
    __tablename__ = "sp_shipment_milestones"
    shipment_reference = Column(String(80), nullable=False, index=True)
    supplier_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=True)
    purchase_order_id = Column(String(36), nullable=True)
    milestone_type = Column(String(30), nullable=False)
    planned_at = Column(DateTime(timezone=True), nullable=True)
    actual_at = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(150), nullable=True)
    carrier = Column(String(100), nullable=True)
    tracking_number = Column(String(100), nullable=True)
    status = Column(String(20), nullable=False, default="PLANNED")
    delay_reason = Column(Text, nullable=True)
