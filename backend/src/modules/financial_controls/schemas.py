"""Financial control API contracts."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class CloseChecklistCreate(BaseModel):
    period_id: str
    checklist_code: str = Field(min_length=2, max_length=50)
    title: str = Field(min_length=3, max_length=200)
    owner_id: Optional[str] = None
    required: bool = True


class CloseChecklistResponse(CloseChecklistCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    completed: bool
    completed_at: Optional[datetime]
    completed_by_id: Optional[str]
    evidence_reference: Optional[str]
    exception_note: Optional[str]
    status: str
    created_at: datetime


class ChecklistComplete(BaseModel):
    evidence_reference: Optional[str] = None
    exception_note: Optional[str] = None


class CloseReadinessResponse(BaseModel):
    period_id: str
    required_count: int
    completed_count: int
    open_required_count: int
    ready_to_lock: bool


class ApprovalPolicyCreate(BaseModel):
    document_type: str = Field(min_length=2, max_length=50)
    policy_code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=3, max_length=150)
    minimum_amount: Decimal = Field(default=Decimal("0"), ge=0)
    maximum_amount: Optional[Decimal] = Field(default=None, gt=0)
    required_role: str = Field(min_length=2, max_length=80)
    approval_level: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_range(self):
        if self.maximum_amount is not None and self.maximum_amount <= self.minimum_amount:
            raise ValueError("Approval maximum must exceed minimum")
        return self


class ApprovalPolicyResponse(ApprovalPolicyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    active: bool
    created_at: datetime


class ApprovalRequestCreate(BaseModel):
    document_type: str = Field(min_length=2, max_length=50)
    document_id: str
    amount: Decimal = Field(ge=0)


class ApprovalDecision(BaseModel):
    status: str = Field(pattern="^(APPROVED|REJECTED|CANCELLED)$")
    decision_note: Optional[str] = None


class ApprovalRequestResponse(ApprovalRequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    request_number: str
    requested_by_id: str
    policy_id: Optional[str]
    approval_level: int
    status: str
    decided_by_id: Optional[str]
    decided_at: Optional[datetime]
    decision_note: Optional[str]
    created_at: datetime


class CashForecastCreate(BaseModel):
    period_start: date
    period_end: date
    forecast_type: str = Field(pattern="^(INFLOW|OUTFLOW)$")
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=3, max_length=255)
    expected_amount: Decimal = Field(ge=0)
    probability_percent: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    source_type: Optional[str] = None
    source_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("Cash forecast period end must not precede its start")
        return self


class CashForecastResponse(CashForecastCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    status: str
    created_at: datetime


class ReconciliationExceptionCreate(BaseModel):
    account_id: Optional[str] = None
    statement_reference: str = Field(min_length=2, max_length=100)
    transaction_date: date
    book_amount: Decimal
    statement_amount: Decimal
    exception_type: str = Field(pattern="^(AMOUNT_MISMATCH|MISSING_BOOK|MISSING_STATEMENT|DUPLICATE)$")
    description: str = Field(min_length=3)
    assigned_to_id: Optional[str] = None


class ReconciliationExceptionResponse(ReconciliationExceptionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    variance_amount: Decimal
    status: str
    resolved_at: Optional[datetime]
    resolved_by_id: Optional[str]
    resolution_note: Optional[str]
    created_at: datetime


class ReconciliationResolution(BaseModel):
    resolution_note: str = Field(min_length=3)
