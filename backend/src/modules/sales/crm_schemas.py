"""Advanced CRM API validation contracts."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OpportunityCreate(BaseModel):
    lead_id: Optional[str] = None
    customer_id: Optional[str] = None
    name: str = Field(min_length=3, max_length=200)
    stage_code: str = "QUALIFICATION"
    amount: Decimal = Field(default=Decimal("0"), ge=0)
    probability_percent: int = Field(default=20, ge=0, le=100)
    expected_close_date: Optional[date] = None
    source: Optional[str] = None
    owner_id: Optional[str] = None
    competitor: Optional[str] = None
    next_step: Optional[str] = None
    notes: Optional[str] = None


class OpportunityUpdate(BaseModel):
    stage_code: Optional[str] = None
    amount: Optional[Decimal] = Field(default=None, ge=0)
    probability_percent: Optional[int] = Field(default=None, ge=0, le=100)
    expected_close_date: Optional[date] = None
    next_step: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(OPEN|WON|LOST|ON_HOLD)$")
    loss_reason: Optional[str] = None


class OpportunityResponse(OpportunityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    opportunity_number: str
    last_contact_at: Optional[datetime]
    status: str
    loss_reason: Optional[str]
    created_at: datetime


class ActivityCreate(BaseModel):
    opportunity_id: Optional[str] = None
    lead_id: Optional[str] = None
    activity_type: str = Field(pattern="^(CALL|EMAIL|MEETING|DEMO|NOTE|TASK)$")
    subject: str = Field(min_length=2, max_length=200)
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    owner_id: Optional[str] = None
    outcome: Optional[str] = None

    @model_validator(mode="after")
    def require_parent(self):
        if not self.opportunity_id and not self.lead_id:
            raise ValueError("CRM activity requires an opportunity or lead")
        if self.opportunity_id and self.lead_id:
            raise ValueError("CRM activity cannot target both opportunity and lead")
        return self


class ActivityResponse(ActivityCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    completed_at: Optional[datetime]
    created_at: datetime


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    snapshot_date: date
    period_start: date
    period_end: date
    pipeline_amount: Decimal
    weighted_amount: Decimal
    committed_amount: Decimal
    best_case_amount: Decimal
    opportunity_count: int
    status: str
    created_at: datetime
