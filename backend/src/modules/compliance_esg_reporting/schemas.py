"""
ESG & Carbon Emissions Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EmissionLogCreate(BaseModel):
    facility_id: str
    facility_name: str
    reporting_period: str
    scope: str = "SCOPE_2_MARKET_BASED"
    energy_type: str
    consumed_quantity: Decimal
    unit_of_measure: str
    emission_factor_kg_co2e: Decimal

class EmissionLogResponse(EmissionLogCreate):
    id: str
    tenant_id: str
    calculated_metric_tons_co2e: Decimal
    is_verified_by_auditor: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SupplierESGAuditCreate(BaseModel):
    vendor_id: str
    vendor_name: str
    audit_date: date
    environmental_score: int
    social_labor_score: int
    governance_ethics_score: int
    has_iso_14001_cert: bool = False
    has_sbti_commitment: bool = False
    audit_notes: Optional[str] = None
