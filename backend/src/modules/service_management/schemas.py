"""API schemas for service management workflows."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ContractCreate(BaseModel):
    contract_number: str = Field(min_length=3, max_length=50)
    customer_id: Optional[str] = None
    name: str = Field(min_length=2, max_length=200)
    contract_type: str = Field(default="TIME_AND_MATERIALS", pattern="^(TIME_AND_MATERIALS|FIXED_PRICE|WARRANTY)$")
    start_date: date
    end_date: date
    currency: str = Field(default="USD", min_length=3, max_length=3)
    value: Decimal = Field(default=Decimal("0"), ge=0)
    response_hours: Decimal = Field(default=Decimal("24"), gt=0)
    resolution_hours: Decimal = Field(default=Decimal("72"), gt=0)
    included_hours: Decimal = Field(default=Decimal("0"), ge=0)
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("Contract end date must be on or after start date")
        return self


class ContractResponse(ContractCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    consumed_hours: Decimal
    status: str
    created_at: datetime


class AssetCreate(BaseModel):
    asset_number: str = Field(min_length=2, max_length=50)
    customer_id: Optional[str] = None
    serial_number: Optional[str] = None
    item_id: Optional[str] = None
    name: str = Field(min_length=2, max_length=200)
    model: Optional[str] = None
    installed_on: Optional[date] = None
    warranty_end_date: Optional[date] = None
    location: Optional[str] = None
    meter_value: Decimal = Field(default=Decimal("0"), ge=0)
    meter_unit: str = "HOURS"


class AssetResponse(AssetCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    status: str
    created_at: datetime


class TicketCreate(BaseModel):
    customer_id: Optional[str] = None
    contract_id: Optional[str] = None
    asset_id: Optional[str] = None
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=5)
    channel: str = Field(default="PORTAL", pattern="^(PORTAL|EMAIL|PHONE|CHAT|INTERNAL)$")
    priority: str = Field(default="NORMAL", pattern="^(LOW|NORMAL|HIGH|URGENT)$")
    assigned_to_id: Optional[str] = None
    billable: bool = True
    estimated_hours: Decimal = Field(default=Decimal("0"), ge=0)


class TicketStatusUpdate(BaseModel):
    status: str = Field(pattern="^(OPEN|IN_PROGRESS|WAITING_CUSTOMER|RESOLVED|CLOSED|CANCELLED)$")
    resolution_notes: Optional[str] = None


class ActivityCreate(BaseModel):
    employee_id: Optional[str] = None
    activity_type: str = Field(default="WORK", pattern="^(WORK|TRAVEL|PHONE|REMOTE|NOTE)$")
    started_at: datetime
    ended_at: Optional[datetime] = None
    hours: Optional[Decimal] = Field(default=None, ge=0)
    hourly_rate: Decimal = Field(default=Decimal("0"), ge=0)
    description: str = Field(min_length=2)
    billable: bool = True

    @model_validator(mode="after")
    def validate_duration(self):
        if self.ended_at and self.ended_at < self.started_at:
            raise ValueError("Activity end must be after activity start")
        if self.hours is None and self.ended_at is None:
            raise ValueError("Provide hours or an end timestamp")
        return self


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    ticket_number: str
    customer_id: Optional[str]
    contract_id: Optional[str]
    asset_id: Optional[str]
    subject: str
    description: str
    channel: str
    priority: str
    status: str
    assigned_to_id: Optional[str]
    opened_at: datetime
    first_response_at: Optional[datetime]
    resolved_at: Optional[datetime]
    due_at: Optional[datetime]
    billable: bool
    estimated_hours: Decimal
    actual_hours: Decimal
    resolution_notes: Optional[str]
    created_at: datetime


class TicketSummary(BaseModel):
    status: str
    priority: str
    ticket_count: int
    total_hours: Decimal
    overdue_count: int
