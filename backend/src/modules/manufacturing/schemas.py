"""
NexERP Manufacturing Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .enums import WorkCenterType, ProductionOrderStatus, JobCardStatus, MRPOrderType


# Work Center Schemas
class WorkCenterBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    work_center_type: WorkCenterType = WorkCenterType.MACHINE
    hourly_rate: Decimal = Field(default=Decimal("50.0"), ge=0)
    overhead_hourly_rate: Decimal = Field(default=Decimal("20.0"), ge=0)
    capacity_hours_per_day: Decimal = Field(default=Decimal("8.0"), ge=1, le=24)
    efficiency_percentage: Decimal = Field(default=Decimal("100.0"), ge=1, le=200)


class WorkCenterCreate(WorkCenterBase):
    pass


class WorkCenterResponse(WorkCenterBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Routing Schemas
class RoutingOperationCreate(BaseModel):
    sequence_number: int = Field(..., ge=1)
    work_center_id: str
    description: str
    setup_time_mins: Decimal = Field(default=Decimal("15.0"), ge=0)
    run_time_mins_per_unit: Decimal = Field(default=Decimal("5.0"), ge=0)
    teardown_time_mins: Decimal = Field(default=Decimal("10.0"), ge=0)


class RoutingOperationResponse(BaseModel):
    id: str
    sequence_number: int
    work_center_id: str
    description: str
    setup_time_mins: Decimal
    run_time_mins_per_unit: Decimal
    teardown_time_mins: Decimal

    class Config:
        from_attributes = True


class RoutingCreate(BaseModel):
    code: str
    name: str
    item_id: str
    version: str = "1.0"
    operations: List[RoutingOperationCreate] = []


class RoutingResponse(BaseModel):
    id: str
    tenant_id: str
    code: str
    name: str
    item_id: str
    version: str
    operations: List[RoutingOperationResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Bill of Materials (BOM) Schemas
class BOMLineCreate(BaseModel):
    item_id: str
    quantity: Decimal = Field(..., gt=0)
    uom_id: str
    scrap_percentage: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    is_phantom: bool = False
    operation_sequence_number: Optional[int] = None


class BOMLineResponse(BaseModel):
    id: str
    item_id: str
    quantity: Decimal
    uom_id: str
    scrap_percentage: Decimal
    is_phantom: bool
    operation_sequence_number: Optional[int]

    class Config:
        from_attributes = True


class BOMCreate(BaseModel):
    bom_number: str
    item_id: str
    quantity: Decimal = Field(default=Decimal("1.0"), gt=0)
    uom_id: str
    version: str = "1.0"
    is_default: bool = True
    effective_from: date
    effective_to: Optional[date] = None
    lines: List[BOMLineCreate] = Field(..., min_length=1)


class BOMResponse(BaseModel):
    id: str
    tenant_id: str
    bom_number: str
    item_id: str
    quantity: Decimal
    uom_id: str
    version: str
    is_default: bool
    effective_from: date
    effective_to: Optional[date]
    lines: List[BOMLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Production Order Schemas
class ProductionOrderCreate(BaseModel):
    item_id: str
    bom_id: str
    routing_id: Optional[str] = None
    warehouse_id: str
    planned_quantity: Decimal = Field(..., gt=0)
    start_date: date
    due_date: date


class ProductionOrderMaterialResponse(BaseModel):
    id: str
    item_id: str
    required_quantity: Decimal
    issued_quantity: Decimal
    unit_cost: Decimal
    total_cost: Decimal

    class Config:
        from_attributes = True


class ProductionOrderResponse(BaseModel):
    id: str
    tenant_id: str
    order_number: str
    item_id: str
    bom_id: str
    routing_id: Optional[str]
    warehouse_id: str
    planned_quantity: Decimal
    completed_quantity: Decimal
    scrapped_quantity: Decimal
    start_date: date
    due_date: date
    status: ProductionOrderStatus
    total_material_cost: Decimal
    total_labor_cost: Decimal
    total_overhead_cost: Decimal
    total_production_cost: Decimal
    unit_cost: Decimal
    materials: List[ProductionOrderMaterialResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Job Card Schemas
class JobCardTimeLogCreate(BaseModel):
    start_time: datetime
    end_time: datetime
    duration_hours: Decimal = Field(..., gt=0)


class JobCardResponse(BaseModel):
    id: str
    job_card_number: str
    production_order_id: str
    operation_id: str
    work_center_id: str
    planned_quantity: Decimal
    completed_quantity: Decimal
    scrapped_quantity: Decimal
    status: JobCardStatus

    class Config:
        from_attributes = True


# MRP Schemas
class MRPRunRequest(BaseModel):
    planning_horizon_days: int = Field(default=90, ge=7, le=365)


class MRPPlannedOrderResponse(BaseModel):
    id: str
    item_id: str
    order_type: MRPOrderType
    suggested_order_date: date
    required_date: date
    quantity: Decimal
    estimated_cost: Decimal
    source_demand_type: Optional[str]

    class Config:
        from_attributes = True


class MRPSnapshotResponse(BaseModel):
    id: str
    tenant_id: str
    snapshot_date: date
    status: str
    total_planned_orders: int
    planned_orders: List[MRPPlannedOrderResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
