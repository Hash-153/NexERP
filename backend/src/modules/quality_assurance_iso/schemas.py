"""
Quality Assurance ISO Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class FMEARecordCreate(BaseModel):
    item_sku: str
    process_step: str
    potential_failure_mode: str
    potential_effect_of_failure: str
    severity: int = Field(..., ge=1, le=10)
    occurrence: int = Field(..., ge=1, le=10)
    detection: int = Field(..., ge=1, le=10)
    recommended_action: Optional[str] = None
