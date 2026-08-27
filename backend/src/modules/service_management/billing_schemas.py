"""Service billing and escalation API contracts."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class ChargeCreate(BaseModel):
    ticket_id: str
    contract_id: Optional[str] = None
    charge_date: date
    charge_type: str = Field(pattern="^(LABOR|TRAVEL|MATERIAL|EXPENSE|FIXED_FEE)$")
    description: str = Field(min_length=2, max_length=255)
    quantity: Decimal = Field(gt=0)
    unit_price: Decimal = Field(ge=0)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    notes: Optional[str] = None


class ChargeResponse(ChargeCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    net_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    invoice_id: Optional[str]
    created_at: datetime


class ChargeStatusUpdate(BaseModel):
    status: str = Field(pattern="^(DRAFT|APPROVED|REJECTED|INVOICED|VOID)$")


class InvoiceBatchCreate(BaseModel):
    customer_id: Optional[str] = None
    period_start: date
    period_end: date
    currency: str = Field(default="USD", min_length=3, max_length=3)

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("Invoice period end must not precede its start")
        return self


class InvoiceBatchResponse(InvoiceBatchCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    batch_number: str
    charge_count: Decimal
    net_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    posted_at: Optional[datetime]
    created_at: datetime


class EscalationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    ticket_id: str
    contract_id: Optional[str]
    escalation_level: str
    trigger: str
    threshold_percent: Decimal
    detected_at: datetime
    acknowledged_at: Optional[datetime]
    acknowledged_by_id: Optional[str]
    owner_id: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime


class EscalationAcknowledge(BaseModel):
    notes: Optional[str] = None
