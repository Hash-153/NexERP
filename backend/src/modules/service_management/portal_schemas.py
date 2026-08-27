"""Customer portal request and conversation contracts."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator


class AppointmentRequestCreate(BaseModel):
    ticket_id: str
    customer_id: str
    preferred_start: datetime
    preferred_end: datetime
    alternate_start: Optional[datetime] = None
    alternate_end: Optional[datetime] = None
    timezone_name: str = "UTC"
    contact_name: str = Field(min_length=2, max_length=150)
    contact_phone: Optional[str] = None
    access_instructions: Optional[str] = None

    @model_validator(mode="after")
    def validate_windows(self):
        if self.preferred_end <= self.preferred_start:
            raise ValueError("Preferred appointment end must be after its start")
        if (self.alternate_start is None) != (self.alternate_end is None):
            raise ValueError("Alternate appointment requires both start and end")
        if self.alternate_start and self.alternate_end and self.alternate_end <= self.alternate_start:
            raise ValueError("Alternate appointment end must be after its start")
        return self


class AppointmentReview(BaseModel):
    status: str = Field(pattern="^(CONFIRMED|DECLINED|RESCHEDULE_REQUIRED|CANCELLED)$")
    review_notes: Optional[str] = None


class AppointmentResponse(AppointmentRequestCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    status: str
    reviewed_at: Optional[datetime]
    reviewed_by_id: Optional[str]
    review_notes: Optional[str]
    created_at: datetime


class ConversationCreate(BaseModel):
    ticket_id: str
    customer_id: str
    message: str = Field(min_length=1, max_length=10000)
    attachment_count: int = Field(default=0, ge=0, le=20)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    tenant_id: str
    ticket_id: str
    customer_id: str
    author_type: str
    author_id: Optional[str]
    message: str
    sent_at: datetime
    is_internal: bool
    attachment_count: str
    created_at: datetime


class PortalTokenResponse(BaseModel):
    token: str
    expires_at: datetime
    customer_id: str
    label: Optional[str]
