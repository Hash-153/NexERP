"""
NexERP Inventory, Multi-Bin Warehouse (WMS) & Cost Valuation Database Models.
Implements FIFO lot queues, moving weighted average costing, multi-location bin coordinates, and cycle counting.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class UnitOfMeasure(Base):
    """
    Standard Unit of Measure (e.g. EA, KG, MTR, LTR, BOX).
    """
    __tablename__ = "inv_units_of_measure"

    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, doc="Weight, Length, Volume, Quantity, Time")


class UOMConversion(Base):
    """
    Conversion matrix factor between two UOMs (e.g. 1 BOX = 24 EA).
    """
    __tablename__ = "inv_uom_conversions"

    from_uom_id = Column(String(36), ForeignKey("inv_units_of_measure.id", ondelete="CASCADE"), nullable=False)
    to_uom_id = Column(String(36), ForeignKey("inv_units_of_measure.id", ondelete="CASCADE"), nullable=False)
    conversion_factor = Column(Numeric(18, 8), nullable=False)


class ItemCategory(Base):
    """
    Item classification category defining default valuation method and GL accounts.
    """
    __tablename__ = "inv_item_categories"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    valuation_method = Column(String(30), default="FIFO", nullable=False, doc="FIFO, MOVING_AVERAGE, STANDARD_COST")
    
    inventory_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="GL Inventory Asset account")
    cogs_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="GL Cost of Goods Sold account")
    variance_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="GL Price/Cost Variance account")

    items = relationship("Item", back_populates="category")


class Item(Base):
    """
    Item / Product Master catalog record.
    """
    __tablename__ = "inv_items"

    sku = Column(String(100), nullable=False, index=True, doc="Stock Keeping Unit / Part Number")
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    barcode = Column(String(100), nullable=True, index=True)
    
    category_id = Column(String(36), ForeignKey("inv_item_categories.id"), nullable=False)
    uom_id = Column(String(36), ForeignKey("inv_units_of_measure.id"), nullable=False)
    item_type = Column(String(30), default="RAW_MATERIAL", nullable=False, doc="RAW_MATERIAL, WORK_IN_PROGRESS, FINISHED_GOOD, CONSUMABLE")
    
    is_serialized = Column(Boolean, default=False, nullable=False)
    is_batch_tracked = Column(Boolean, default=False, nullable=False)
    
    min_stock_level = Column(Numeric(18, 4), default=0.0, nullable=False)
    max_stock_level = Column(Numeric(18, 4), default=0.0, nullable=False)
    reorder_point = Column(Numeric(18, 4), default=10.0, nullable=False)
    safety_stock = Column(Numeric(18, 4), default=5.0, nullable=False)
    lead_time_days = Column(Integer, default=7, nullable=False)
    
    standard_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    moving_average_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    list_price = Column(Numeric(18, 4), default=0.0, nullable=False)

    category = relationship("ItemCategory", back_populates="items")
    uom = relationship("UnitOfMeasure")
    balances = relationship("StockItemBalance", back_populates="item", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_inv_item_tenant_sku", "tenant_id", "sku", unique=True),
    )


class Warehouse(Base):
    """
    Physical distribution center or plant facility.
    """
    __tablename__ = "inv_warehouses"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    address = Column(Text, nullable=True)
    is_quarantine = Column(Boolean, default=False, nullable=False)
    is_transit = Column(Boolean, default=False, nullable=False)

    locations = relationship("WarehouseLocation", back_populates="warehouse", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_inv_warehouse_tenant_code", "tenant_id", "code", unique=True),
    )


class WarehouseLocation(Base):
    """
    Specific coordinate location (Zone - Aisle - Rack - Shelf - Bin).
    """
    __tablename__ = "inv_warehouse_locations"

    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id", ondelete="CASCADE"), nullable=False)
    location_code = Column(String(100), nullable=False, index=True, doc="e.g. 'Z1-A04-R02-B08'")
    zone = Column(String(50), default="General", nullable=False)
    aisle = Column(String(20), nullable=True)
    rack = Column(String(20), nullable=True)
    shelf = Column(String(20), nullable=True)
    bin = Column(String(20), nullable=True)
    max_weight_capacity_kg = Column(Numeric(18, 4), nullable=True)

    warehouse = relationship("Warehouse", back_populates="locations")


class StockLot(Base):
    """
    Batch / Lot tracking record with expiration and manufacturer tracking.
    """
    __tablename__ = "inv_stock_lots"

    item_id = Column(String(36), ForeignKey("inv_items.id", ondelete="CASCADE"), nullable=False)
    lot_number = Column(String(100), nullable=False, index=True)
    manufacture_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True, index=True)
    supplier_lot_number = Column(String(100), nullable=True)

    item = relationship("Item")


class StockItemBalance(Base):
    """
    Real-time inventory level at a specific warehouse location.
    """
    __tablename__ = "inv_stock_balances"

    item_id = Column(String(36), ForeignKey("inv_items.id", ondelete="CASCADE"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id", ondelete="CASCADE"), nullable=False)
    location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id", ondelete="CASCADE"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inv_stock_lots.id"), nullable=True)
    
    quantity_on_hand = Column(Numeric(18, 4), default=0.0, nullable=False)
    quantity_reserved = Column(Numeric(18, 4), default=0.0, nullable=False)
    quantity_available = Column(Numeric(18, 4), default=0.0, nullable=False)

    item = relationship("Item", back_populates="balances")
    warehouse = relationship("Warehouse")
    location = relationship("WarehouseLocation")
    lot = relationship("StockLot")


class StockValuationLayer(Base):
    """
    FIFO queue layer recording cost basis and residual quantities for inventory accounting.
    """
    __tablename__ = "inv_stock_valuation_layers"

    item_id = Column(String(36), ForeignKey("inv_items.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inv_stock_lots.id"), nullable=True)
    
    receipt_date = Column(Date, nullable=False, index=True)
    initial_quantity = Column(Numeric(18, 4), nullable=False)
    remaining_quantity = Column(Numeric(18, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), nullable=False)
    total_value = Column(Numeric(18, 4), nullable=False)
    
    source_document_type = Column(String(50), nullable=True, doc="GoodsReceiptNote, ProductionOutput, Adjustment")
    source_document_id = Column(String(36), nullable=True)


class StockMovement(Base):
    """
    Inventory movement transaction header (Receipt, Issue, Transfer, Adjustment).
    """
    __tablename__ = "inv_stock_movements"

    movement_number = Column(String(50), nullable=False, index=True, doc="e.g. 'STK-2026-0001'")
    movement_type = Column(String(50), nullable=False, index=True)
    movement_date = Column(Date, nullable=False)
    
    source_warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=True)
    target_warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=True)
    
    status = Column(String(30), default="POSTED", nullable=False)
    reference = Column(String(100), nullable=True)
    remarks = Column(Text, nullable=True)
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)

    lines = relationship("StockMovementLine", back_populates="movement", cascade="all, delete-orphan")


class StockMovementLine(Base):
    """
    Individual line item in an inventory stock transaction.
    """
    __tablename__ = "inv_stock_movement_lines"

    stock_movement_id = Column(String(36), ForeignKey("inv_stock_movements.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    
    source_location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id"), nullable=True)
    target_location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id"), nullable=True)
    lot_id = Column(String(36), ForeignKey("inv_stock_lots.id"), nullable=True)
    
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), nullable=False)
    total_cost = Column(Numeric(18, 4), nullable=False)

    movement = relationship("StockMovement", back_populates="lines")
    item = relationship("Item")


class CycleCountSheet(Base):
    """
    Physical Inventory counting sheet for periodic stock audits.
    """
    __tablename__ = "inv_cycle_count_sheets"

    sheet_number = Column(String(50), nullable=False, index=True)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    count_date = Column(Date, nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False, doc="DRAFT, IN_PROGRESS, APPROVED, CANCELLED")
    supervisor_id = Column(String(36), nullable=True)
    notes = Column(Text, nullable=True)

    lines = relationship("CycleCountLine", back_populates="sheet", cascade="all, delete-orphan")


class CycleCountLine(Base):
    """
    Discrepancy audit row comparing physical count against recorded book balance.
    """
    __tablename__ = "inv_cycle_count_lines"

    sheet_id = Column(String(36), ForeignKey("inv_cycle_count_sheets.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inv_stock_lots.id"), nullable=True)
    
    system_quantity = Column(Numeric(18, 4), nullable=False)
    counted_quantity = Column(Numeric(18, 4), nullable=False)
    variance_quantity = Column(Numeric(18, 4), nullable=False)
    unit_cost = Column(Numeric(18, 4), nullable=False)
    variance_cost = Column(Numeric(18, 4), nullable=False)

    sheet = relationship("CycleCountSheet", back_populates="lines")
    item = relationship("Item")
