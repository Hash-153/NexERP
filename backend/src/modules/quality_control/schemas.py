"""
NexERP Quality Control Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .enums import InspectionType, TestType, InspectionStatus, NCRStatus


# Quality Parameter Schemas
class QualityParameterBase(BaseModel):
    parameter_name: str = Field(..., min_length=2, max_length=150)
    test_type: TestType = TestType.NUMERIC_RANGE
    min_value: Optional[Decimal] = None
    max_value: Optional[Decimal] = None
    target_value: Optional[str] = None
    is_critical: bool = False


class QualityParameterCreate(QualityParameterBase):
    pass


class QualityParameterResponse(QualityParameterBase):
    id: str
    inspection_plan_id: str

    class Config:
        from_attributes = True


# Quality Plan Schemas
class QualityPlanBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    item_id: Optional[str] = None
    inspection_type: InspectionType = InspectionType.INCOMING_RECEIPT
    sample_size_percentage: Decimal = Field(default=Decimal("10.0"), ge=1, le=100)
    pass_threshold_percentage: Decimal = Field(default=Decimal("95.0"), ge=50, le=100)


class QualityPlanCreate(QualityPlanBase):
    parameters: List[QualityParameterCreate] = []


class QualityPlanResponse(QualityPlanBase):
    id: str
    tenant_id: str
    parameters: List[QualityParameterResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Inspection Record Schemas
class InspectionResultLineCreate(BaseModel):
    parameter_id: str
    measured_numeric_value: Optional[Decimal] = None
    pass_fail_result: bool = True
    remarks: Optional[str] = None


class InspectionResultLineResponse(BaseModel):
    id: str
    parameter_id: str
    measured_numeric_value: Optional[Decimal]
    pass_fail_result: bool
    is_conforming: bool
    remarks: Optional[str]

    class Config:
        from_attributes = True


class InspectionRecordCreate(BaseModel):
    plan_id: str
    item_id: str
    source_document_type: Optional[str] = None
    source_document_id: Optional[str] = None
    inspection_date: date
    inspected_quantity: Decimal = Field(..., gt=0)
    passed_quantity: Decimal = Field(..., ge=0)
    rejected_quantity: Decimal = Field(default=Decimal("0.0"), ge=0)
    remarks: Optional[str] = None
    results: List[InspectionResultLineCreate] = []


class InspectionRecordResponse(BaseModel):
    id: str
    tenant_id: str
    inspection_number: str
    plan_id: str
    item_id: str
    source_document_type: Optional[str]
    source_document_id: Optional[str]
    inspection_date: date
    inspected_quantity: Decimal
    passed_quantity: Decimal
    rejected_quantity: Decimal
    status: InspectionStatus
    remarks: Optional[str]
    results: List[InspectionResultLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# NCR Schemas
class NCRCreate(BaseModel):
    inspection_record_id: Optional[str] = None
    item_id: str
    issue_summary: str = Field(..., min_length=5, max_length=255)
    root_cause_analysis: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    assigned_to_id: Optional[str] = None


class NCRResponse(BaseModel):
    id: str
    tenant_id: str
    ncr_number: str
    inspection_record_id: Optional[str]
    item_id: str
    issue_summary: str
    root_cause_analysis: Optional[str]
    containment_action: Optional[str]
    corrective_action: Optional[str]
    status: NCRStatus
    assigned_to_id: Optional[str]
    closed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
