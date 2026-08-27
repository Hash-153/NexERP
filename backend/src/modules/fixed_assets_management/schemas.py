"""
Fixed Assets Management Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class FixedAssetMasterCreate(BaseModel):
    asset_tag: str = Field(..., max_length=50)
    serial_number: Optional[str] = None
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    category: str
    acquisition_date: date
    in_service_date: date
    original_acquisition_cost: Decimal
    salvage_scrap_value: Decimal = Decimal("0.0")
    useful_life_months: int = 60
    location_facility: Optional[str] = None
    cost_center_code: Optional[str] = None
    gl_asset_account_id: Optional[str] = None
    gl_depreciation_account_id: Optional[str] = None
    gl_expense_account_id: Optional[str] = None

class FixedAssetMasterResponse(FixedAssetMasterCreate):
    id: str
    tenant_id: str
    status: str
    current_net_book_value: Decimal
    accumulated_depreciation: Decimal
    accumulated_impairment: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DepreciationRunRequest(BaseModel):
    fiscal_period: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    book_type: str = "CORPORATE_GAAP"
    depreciation_method: str = "STRAIGHT_LINE"

class PhysicalAuditScan(BaseModel):
    asset_id: str
    audit_batch_code: str
    detected_location: str
    condition_rating: str = "GOOD"
    notes: Optional[str] = None
