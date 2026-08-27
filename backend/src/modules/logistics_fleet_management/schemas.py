"""
Logistics & Fleet Management Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FreightCarrierCreate(BaseModel):
    carrier_code: str
    company_name: str
    scac_code: Optional[str] = None
    dot_number: Optional[str] = None
    transport_mode: str = "ROAD_FTL"
    contact_email: str
    contact_phone: Optional[str] = None
    is_preferred: bool = False

class FreightCarrierResponse(FreightCarrierCreate):
    id: str
    tenant_id: str
    performance_rating: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ShipmentDispatchCreate(BaseModel):
    carrier_id: str
    tracking_bol_number: str
    transport_mode: str = "ROAD_FTL"
    origin_address: str
    destination_address: str
    scheduled_pickup: datetime
    estimated_delivery: datetime
    total_pallets: int = 1
    gross_weight_kg: Decimal
    length_cm: Decimal = Decimal("120.0")
    width_cm: Decimal = Decimal("80.0")
    height_cm: Decimal = Decimal("160.0")
    base_rate_per_kg: Decimal = Decimal("2.50")

class TelematicsPingCreate(BaseModel):
    shipment_id: str
    latitude: Decimal
    longitude: Decimal
    speed_kmh: Decimal = Decimal("0.0")
    temperature_c: Optional[Decimal] = None
