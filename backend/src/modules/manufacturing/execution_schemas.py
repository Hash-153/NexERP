"""Manufacturing execution API contracts."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OperatorSessionCreate(BaseModel):
    job_card_id: str
    operator_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    break_minutes: int = Field(default=0, ge=0)
    hourly_rate: Decimal = Field(default=Decimal("0"), ge=0)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_times(self):
        if self.ended_at and self.ended_at <= self.started_at:
            raise ValueError("Operator session end must be after its start")
        return self


class OperatorSessionResponse(OperatorSessionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    productive_hours: Decimal
    labor_cost: Decimal
    status: str
    created_at: datetime


class QualityCheckCreate(BaseModel):
    production_order_id: str
    job_card_id: Optional[str] = None
    checkpoint_code: str = Field(min_length=2, max_length=50)
    checkpoint_name: str = Field(min_length=2, max_length=150)
    sample_size: Decimal = Field(gt=0)
    accepted_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    rejected_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    measurement_value: Optional[Decimal] = None
    lower_specification: Optional[Decimal] = None
    upper_specification: Optional[Decimal] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_sample(self):
        if self.accepted_quantity + self.rejected_quantity > self.sample_size:
            raise ValueError("Accepted and rejected quantities cannot exceed sample size")
        if self.lower_specification is not None and self.upper_specification is not None and self.upper_specification < self.lower_specification:
            raise ValueError("Upper specification must not be below lower specification")
        return self


class QualityCheckResponse(QualityCheckCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    inspector_id: Optional[str]
    checked_at: datetime
    result: str
    created_at: datetime


class DowntimeCreate(BaseModel):
    work_center_id: str
    production_order_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    category: str = Field(pattern="^(BREAKDOWN|MATERIAL_SHORTAGE|CHANGEOVER|QUALITY|PLANNED|OTHER)$")
    reason_code: str = Field(min_length=2, max_length=50)
    reason_detail: Optional[str] = None
    planned: bool = False


class ScrapCreate(BaseModel):
    production_order_id: str
    job_card_id: Optional[str] = None
    quantity: Decimal = Field(gt=0)
    unit_cost: Decimal = Field(ge=0)
    reason_code: str = Field(min_length=2, max_length=50)
    explanation: str = Field(min_length=5)


class ScrapDecision(BaseModel):
    status: str = Field(pattern="^(APPROVED|REJECTED)$")
    disposition: Optional[str] = None


class ScrapResponse(ScrapCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    total_cost: Decimal
    requested_by_id: str
    requested_at: datetime
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]
    status: str
    disposition: Optional[str]
    created_at: datetime
