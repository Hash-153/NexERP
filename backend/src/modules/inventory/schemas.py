"""
NexERP Inventory Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .enums import ItemType, ValuationMethod, MovementType, CycleCountStatus


# Unit of Measure Schemas
class UOMBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=2, max_length=100)
    category: str = "Quantity"


class UOMCreate(UOMBase):
    pass


class UOMResponse(UOMBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Item Category Schemas
class ItemCategoryBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=100)
    valuation_method: ValuationMethod = ValuationMethod.FIFO
    inventory_account_id: Optional[str] = None
    cogs_account_id: Optional[str] = None
    variance_account_id: Optional[str] = None


class ItemCategoryCreate(ItemCategoryBase):
    pass


class ItemCategoryResponse(ItemCategoryBase):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# Item Schemas
class ItemBase(BaseModel):
    sku: str = Field(..., min_length=2, max_length=100)
    name: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    barcode: Optional[str] = None
    category_id: str
    uom_id: str
    item_type: ItemType = ItemType.RAW_MATERIAL
    is_serialized: bool = False
    is_batch_tracked: bool = False
    min_stock_level: Decimal = Field(default=Decimal("0.0"), ge=0)
    max_stock_level: Decimal = Field(default=Decimal("0.0"), ge=0)
    reorder_point: Decimal = Field(default=Decimal("10.0"), ge=0)
    safety_stock: Decimal = Field(default=Decimal("5.0"), ge=0)
    lead_time_days: int = Field(default=7, ge=0)
    standard_cost: Decimal = Field(default=Decimal("0.0"), ge=0)
    list_price: Decimal = Field(default=Decimal("0.0"), ge=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    barcode: Optional[str] = None
    min_stock_level: Optional[Decimal] = None
    max_stock_level: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    safety_stock: Optional[Decimal] = None
    lead_time_days: Optional[int] = None
    standard_cost: Optional[Decimal] = None
    list_price: Optional[Decimal] = None


class ItemResponse(ItemBase):
    id: str
    tenant_id: str
    moving_average_cost: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Warehouse & Location Schemas
class WarehouseLocationBase(BaseModel):
    location_code: str
    zone: str = "General"
    aisle: Optional[str] = None
    rack: Optional[str] = None
    shelf: Optional[str] = None
    bin: Optional[str] = None
    max_weight_capacity_kg: Optional[Decimal] = None


class WarehouseLocationCreate(WarehouseLocationBase):
    pass


class WarehouseLocationResponse(WarehouseLocationBase):
    id: str
    warehouse_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class WarehouseBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    address: Optional[str] = None
    is_quarantine: bool = False
    is_transit: bool = False


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: str
    tenant_id: str
    locations: List[WarehouseLocationResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Stock Movement Schemas
class StockMovementLineCreate(BaseModel):
    item_id: str
    source_location_id: Optional[str] = None
    target_location_id: Optional[str] = None
    lot_id: Optional[str] = None
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Optional[Decimal] = Field(default=Decimal("0.0"), ge=0)


class StockMovementLineResponse(BaseModel):
    id: str
    item_id: str
    source_location_id: Optional[str]
    target_location_id: Optional[str]
    lot_id: Optional[str]
    quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal

    class Config:
        from_attributes = True


class StockMovementCreate(BaseModel):
    movement_type: MovementType
    movement_date: date
    source_warehouse_id: Optional[str] = None
    target_warehouse_id: Optional[str] = None
    reference: Optional[str] = None
    remarks: Optional[str] = None
    lines: List[StockMovementLineCreate] = Field(..., min_length=1)


class StockMovementResponse(BaseModel):
    id: str
    tenant_id: str
    movement_number: str
    movement_type: MovementType
    movement_date: date
    source_warehouse_id: Optional[str]
    target_warehouse_id: Optional[str]
    status: str
    reference: Optional[str]
    remarks: Optional[str]
    journal_entry_id: Optional[str]
    lines: List[StockMovementLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Stock Balance & Valuation Schemas
class StockBalanceResponse(BaseModel):
    id: str
    item_id: str
    warehouse_id: str
    location_id: str
    lot_id: Optional[str]
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    quantity_available: Decimal

    class Config:
        from_attributes = True


class ValuationLayerResponse(BaseModel):
    id: str
    item_id: str
    warehouse_id: str
    receipt_date: date
    initial_quantity: Decimal
    remaining_quantity: Decimal
    unit_cost: Decimal
    total_value: Decimal

    class Config:
        from_attributes = True


# Cycle Count Schemas
class CycleCountLineCreate(BaseModel):
    item_id: str
    location_id: str
    lot_id: Optional[str] = None
    counted_quantity: Decimal = Field(..., ge=0)


class CycleCountSheetCreate(BaseModel):
    warehouse_id: str
    count_date: date
    notes: Optional[str] = None
    lines: List[CycleCountLineCreate] = []


class CycleCountLineResponse(BaseModel):
    id: str
    item_id: str
    location_id: str
    lot_id: Optional[str]
    system_quantity: Decimal
    counted_quantity: Decimal
    variance_quantity: Decimal
    unit_cost: Decimal
    variance_cost: Decimal

    class Config:
        from_attributes = True


class CycleCountSheetResponse(BaseModel):
    id: str
    tenant_id: str
    sheet_number: str
    warehouse_id: str
    count_date: date
    status: CycleCountStatus
    supervisor_id: Optional[str]
    notes: Optional[str]
    lines: List[CycleCountLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
