"""Validation contracts for field service operations."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class TechnicianCreate(BaseModel):
    employee_id: Optional[str] = None
    technician_code: str = Field(min_length=2, max_length=40)
    display_name: str = Field(min_length=2, max_length=150)
    territory: Optional[str] = None
    skill_group: Optional[str] = None
    phone: Optional[str] = None
    hourly_cost: Decimal = Field(default=Decimal("0"), ge=0)
    hourly_rate: Decimal = Field(default=Decimal("0"), ge=0)
    utilization_target: Decimal = Field(default=Decimal("75"), ge=0, le=100)


class TechnicianResponse(TechnicianCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    status: str
    created_at: datetime


class DispatchCreate(BaseModel):
    ticket_id: str
    technician_id: Optional[str] = None
    scheduled_start: datetime
    scheduled_end: datetime
    address: Optional[str] = None
    visit_type: str = Field(default="ON_SITE", pattern="^(ON_SITE|REMOTE|DEPOT)$")
    travel_minutes: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_schedule(self):
        if self.scheduled_end <= self.scheduled_start:
            raise ValueError("Dispatch end must be after dispatch start")
        return self


class DispatchStatusUpdate(BaseModel):
    status: str = Field(pattern="^(PLANNED|CONFIRMED|EN_ROUTE|ON_SITE|COMPLETED|CANCELLED)$")
    notes: Optional[str] = None


class DispatchResponse(DispatchCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    dispatch_number: str
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    status: str
    arrival_notes: Optional[str]
    completion_notes: Optional[str]
    created_at: datetime


class MaintenancePlanCreate(BaseModel):
    asset_id: str
    plan_number: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=200)
    frequency_days: int = Field(gt=0, le=3650)
    next_due_date: date
    estimated_hours: Decimal = Field(default=Decimal("1"), gt=0)
    checklist: Optional[str] = None


class MaintenancePlanResponse(MaintenancePlanCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    last_completed_date: Optional[date]
    status: str
    created_at: datetime


class ArticleCreate(BaseModel):
    article_number: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=20)
    category: str = Field(default="GENERAL", min_length=2, max_length=80)
    audience: str = Field(default="INTERNAL", pattern="^(INTERNAL|CUSTOMER|BOTH)$")


class ArticleResponse(ArticleCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    version: int
    published_at: Optional[datetime]
    view_count: int
    helpful_count: int
    status: str
    created_at: datetime


class FeedbackCreate(BaseModel):
    ticket_id: str
    customer_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    response_time_rating: Optional[int] = Field(default=None, ge=1, le=5)
    resolution_rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)
    is_public: bool = False


class FeedbackResponse(FeedbackCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    submitted_at: datetime
    created_at: datetime
