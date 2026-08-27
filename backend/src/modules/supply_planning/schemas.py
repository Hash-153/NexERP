"""Supply planning validation contracts."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ForecastCreate(BaseModel):
    item_id: str
    warehouse_id: Optional[str] = None
    period_start: date
    period_end: date
    forecast_quantity: Decimal = Field(gt=0)
    baseline_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    promotion_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    confidence_percent: Decimal = Field(default=Decimal("50"), ge=0, le=100)
    method: str = "MOVING_AVERAGE"

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("Forecast period end must not precede its start")
        return self


class ForecastResponse(ForecastCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    actual_quantity: Optional[Decimal]
    status: str
    created_at: datetime


class PolicyCreate(BaseModel):
    item_id: str
    warehouse_id: str
    planning_method: str = Field(default="MIN_MAX", pattern="^(MIN_MAX|PERIODIC_REVIEW|MRP|KANBAN)$")
    review_period_days: int = Field(default=7, gt=0)
    lead_time_days: int = Field(default=7, ge=0)
    safety_stock_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    reorder_point_quantity: Decimal = Field(default=Decimal("0"), ge=0)
    minimum_order_quantity: Decimal = Field(default=Decimal("1"), gt=0)
    maximum_order_quantity: Optional[Decimal] = Field(default=None, gt=0)
    order_multiple: Decimal = Field(default=Decimal("1"), gt=0)
    preferred_supplier_id: Optional[str] = None


class PolicyResponse(PolicyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    active: bool
    created_at: datetime


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    recommendation_number: str
    item_id: str
    warehouse_id: str
    supplier_id: Optional[str]
    required_date: date
    demand_quantity: Decimal
    available_quantity: Decimal
    safety_stock_quantity: Decimal
    recommended_quantity: Decimal
    estimated_unit_cost: Decimal
    estimated_total_cost: Decimal
    reason: str
    priority: str
    status: str
    created_at: datetime


class ScorecardCreate(BaseModel):
    supplier_id: str
    period_start: date
    period_end: date
    order_count: int = Field(ge=0)
    on_time_count: int = Field(ge=0)
    received_quantity: Decimal = Field(ge=0)
    accepted_quantity: Decimal = Field(ge=0)
    spend_amount: Decimal = Field(ge=0)


class ScorecardResponse(ScorecardCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    on_time_percent: Decimal
    quality_percent: Decimal
    composite_score: Decimal
    status: str
    created_at: datetime


class MilestoneCreate(BaseModel):
    shipment_reference: str = Field(min_length=2, max_length=80)
    supplier_id: Optional[str] = None
    purchase_order_id: Optional[str] = None
    milestone_type: str = Field(pattern="^(BOOKED|PICKED_UP|IN_TRANSIT|CUSTOMS|DELIVERED)$")
    planned_at: Optional[datetime] = None
    location: Optional[str] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None


class MilestoneResponse(MilestoneCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    actual_at: Optional[datetime]
    status: str
    delay_reason: Optional[str]
    created_at: datetime
