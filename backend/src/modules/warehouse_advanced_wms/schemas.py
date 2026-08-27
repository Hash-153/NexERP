"""
Advanced WMS Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class WarehouseZoneCreate(BaseModel):
    warehouse_id: str
    zone_code: str
    name: str
    zone_type: str = "HIGH_BAY_RACK"
    temperature_min_c: Optional[Decimal] = None
    temperature_max_c: Optional[Decimal] = None
    is_bonded: bool = False
    is_hazardous: bool = False

class WarehouseZoneResponse(WarehouseZoneCreate):
    id: str
    tenant_id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class WarehouseLocationCreate(BaseModel):
    zone_id: str
    location_barcode: str
    aisle: str
    bay: str
    shelf: str
    bin: str
    max_weight_kg: Decimal = Decimal("1000.0")
    max_volume_cbm: Decimal = Decimal("2.5")
    velocity_class: str = "B"

class WarehouseLocationResponse(WarehouseLocationCreate):
    id: str
    current_weight_kg: Decimal
    occupied_volume_cbm: Decimal
    is_blocked: bool
    is_pick_face: bool
    model_config = ConfigDict(from_attributes=True)

class WaveBatchCreate(BaseModel):
    carrier_cutoff_time: Optional[datetime] = None
    priority_level: int = 5
    order_ids: List[str]

class WaveBatchResponse(BaseModel):
    id: str
    wave_number: str
    status: str
    total_lines: int
    picked_lines: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PickExecutionRequest(BaseModel):
    task_id: str
    picked_qty: Decimal
    scanned_barcode: str
    tote_license_plate: str
