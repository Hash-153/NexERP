"""
NexERP Manufacturing, Bill of Materials (BOM), Work Centers & MRP-II Database Models.
Implements multi-level BOM explosion, finite capacity work centers, production orders with backflushing, and MRP demand scheduling.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class WorkCenter(Base):
    """
    Manufacturing resource (machine, assembly line, or labor crew) with capacity and costing rates.
    """
    __tablename__ = "mfg_work_centers"

    code = Column(String(50), nullable=False, index=True, doc="e.g. 'WC-CNC-01', 'WC-ASSM-02'")
    name = Column(String(150), nullable=False)
    work_center_type = Column(String(30), default="MACHINE", nullable=False, doc="MACHINE, LABOR, ASSEMBLY, OUTSOURCED")
    
    hourly_rate = Column(Numeric(18, 4), default=50.0, nullable=False, doc="Cost per operating hour")
    overhead_hourly_rate = Column(Numeric(18, 4), default=20.0, nullable=False)
    
    capacity_hours_per_day = Column(Numeric(5, 2), default=8.0, nullable=False)
    efficiency_percentage = Column(Numeric(5, 2), default=100.0, nullable=False)

    operations = relationship("RoutingOperation", back_populates="work_center")


class Routing(Base):
    """
    Sequential sequence of shop-floor manufacturing operations.
    """
    __tablename__ = "mfg_routings"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    version = Column(String(20), default="1.0", nullable=False)

    item = relationship("backend.src.modules.inventory.models.Item")
    operations = relationship("RoutingOperation", back_populates="routing", cascade="all, delete-orphan")


class RoutingOperation(Base):
    """
    Individual step in a routing (Setup, Run, Teardown times).
    """
    __tablename__ = "mfg_routing_operations"

    routing_id = Column(String(36), ForeignKey("mfg_routings.id", ondelete="CASCADE"), nullable=False)
    sequence_number = Column(Integer, nullable=False, doc="10, 20, 30...")
    work_center_id = Column(String(36), ForeignKey("mfg_work_centers.id"), nullable=False)
    
    description = Column(String(255), nullable=False)
    setup_time_mins = Column(Numeric(10, 2), default=15.0, nullable=False)
    run_time_mins_per_unit = Column(Numeric(10, 2), default=5.0, nullable=False)
    teardown_time_mins = Column(Numeric(10, 2), default=10.0, nullable=False)

    routing = relationship("Routing", back_populates="operations")
    work_center = relationship("WorkCenter", back_populates="operations")


class BillOfMaterials(Base):
    """
    Bill of Materials (BOM) recipe defining subassemblies and raw materials.
    """
    __tablename__ = "mfg_boms"

    bom_number = Column(String(50), nullable=False, index=True, doc="e.g. 'BOM-PUMP-001'")
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    uom_id = Column(String(36), ForeignKey("inv_units_of_measure.id"), nullable=False)
    
    version = Column(String(20), default="1.0", nullable=False)
    is_default = Column(Boolean, default=True, nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)

    item = relationship("backend.src.modules.inventory.models.Item")
    uom = relationship("backend.src.modules.inventory.models.UnitOfMeasure")
    lines = relationship("BOMLine", back_populates="bom", cascade="all, delete-orphan")


class BOMLine(Base):
    """
    Component item requirement in a BOM recipe with scrap factor.
    """
    __tablename__ = "mfg_bom_lines"

    bom_id = Column(String(36), ForeignKey("mfg_boms.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    uom_id = Column(String(36), ForeignKey("inv_units_of_measure.id"), nullable=False)
    
    scrap_percentage = Column(Numeric(5, 2), default=0.0, nullable=False, doc="Estimated scrap waste %")
    is_phantom = Column(Boolean, default=False, nullable=False, doc="Phantom subassembly exploded during planning")
    operation_sequence_number = Column(Integer, nullable=True)

    bom = relationship("BillOfMaterials", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")
    uom = relationship("backend.src.modules.inventory.models.UnitOfMeasure")


class ProductionOrder(Base):
    """
    Shop-floor Work Order (WO) authorizing production batch run.
    """
    __tablename__ = "mfg_production_orders"

    order_number = Column(String(50), nullable=False, index=True, doc="e.g. 'WO-2026-0001'")
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    bom_id = Column(String(36), ForeignKey("mfg_boms.id"), nullable=False)
    routing_id = Column(String(36), ForeignKey("mfg_routings.id"), nullable=True)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    
    planned_quantity = Column(Numeric(18, 4), nullable=False)
    completed_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    scrapped_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    start_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(30), default="PLANNED", nullable=False, index=True, doc="PLANNED, RELEASED, IN_PROGRESS, COMPLETED, CANCELLED")
    
    total_material_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_labor_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_overhead_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_production_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    unit_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    stock_movement_id = Column(String(36), ForeignKey("inv_stock_movements.id"), nullable=True)

    item = relationship("backend.src.modules.inventory.models.Item")
    bom = relationship("BillOfMaterials")
    routing = relationship("Routing")
    materials = relationship("ProductionOrderMaterial", back_populates="production_order", cascade="all, delete-orphan")
    job_cards = relationship("JobCard", back_populates="production_order", cascade="all, delete-orphan")


class ProductionOrderMaterial(Base):
    """
    Component raw material allocated and consumed for a Work Order.
    """
    __tablename__ = "mfg_wo_materials"

    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    
    required_quantity = Column(Numeric(18, 4), nullable=False)
    issued_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    unit_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_cost = Column(Numeric(18, 4), default=0.0, nullable=False)

    production_order = relationship("ProductionOrder", back_populates="materials")
    item = relationship("backend.src.modules.inventory.models.Item")


class JobCard(Base):
    """
    Shop-floor work center routing ticket dispatched to machine/labor operators.
    """
    __tablename__ = "mfg_job_cards"

    job_card_number = Column(String(50), nullable=False, index=True)
    production_order_id = Column(String(36), ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False)
    operation_id = Column(String(36), ForeignKey("mfg_routing_operations.id"), nullable=False)
    work_center_id = Column(String(36), ForeignKey("mfg_work_centers.id"), nullable=False)
    
    planned_quantity = Column(Numeric(18, 4), nullable=False)
    completed_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    scrapped_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="PENDING", nullable=False, doc="PENDING, IN_PROGRESS, COMPLETED")

    production_order = relationship("ProductionOrder", back_populates="job_cards")
    operation = relationship("RoutingOperation")
    work_center = relationship("WorkCenter")
    time_logs = relationship("JobCardTimeLog", back_populates="job_card", cascade="all, delete-orphan")


class JobCardTimeLog(Base):
    """
    Operator time tracking record capturing labor and machine machine hours.
    """
    __tablename__ = "mfg_job_card_time_logs"

    job_card_id = Column(String(36), ForeignKey("mfg_job_cards.id", ondelete="CASCADE"), nullable=False)
    operator_id = Column(String(36), nullable=True)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    duration_hours = Column(Numeric(6, 2), nullable=False)
    labor_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    machine_cost = Column(Numeric(18, 4), default=0.0, nullable=False)

    job_card = relationship("JobCard", back_populates="time_logs")


class MRPSnapshot(Base):
    """
    Master Production Schedule / Material Requirements Planning calculation run header.
    """
    __tablename__ = "mfg_mrp_snapshots"

    snapshot_date = Column(Date, nullable=False)
    status = Column(String(30), default="COMPLETED", nullable=False)
    total_planned_orders = Column(Integer, default=0, nullable=False)
    generated_by_id = Column(String(36), nullable=True)

    planned_orders = relationship("MRPPlannedOrder", back_populates="snapshot", cascade="all, delete-orphan")


class MRPPlannedOrder(Base):
    """
    Suggested purchase order or production work order generated by the MRP explosion algorithm.
    """
    __tablename__ = "mfg_mrp_planned_orders"

    mrp_snapshot_id = Column(String(36), ForeignKey("mfg_mrp_snapshots.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    order_type = Column(String(30), nullable=False, doc="PURCHASE, PRODUCTION")
    
    suggested_order_date = Column(Date, nullable=False)
    required_date = Column(Date, nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    estimated_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    source_demand_type = Column(String(50), nullable=True, doc="SalesOrder, SafetyStock, DependentDemand")
    source_demand_id = Column(String(36), nullable=True)

    snapshot = relationship("MRPSnapshot", back_populates="planned_orders")
    item = relationship("backend.src.modules.inventory.models.Item")
