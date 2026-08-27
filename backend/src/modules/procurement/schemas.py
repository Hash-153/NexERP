"""
NexERP Procurement Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .enums import RequisitionStatus, RFQStatus, POStatus, GRNStatus


# Purchase Requisition Schemas
class RequisitionLineCreate(BaseModel):
    item_id: Optional[str] = None
    description: str
    quantity: Decimal = Field(..., gt=0)
    estimated_unit_cost: Decimal = Field(default=Decimal("0.0"), ge=0)


class RequisitionLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: Optional[str]
    description: str
    quantity: Decimal
    estimated_unit_cost: Decimal
    total_estimated_cost: Decimal

    class Config:
        from_attributes = True


class RequisitionCreate(BaseModel):
    department_id: Optional[str] = None
    required_by_date: date
    justification: Optional[str] = None
    lines: List[RequisitionLineCreate] = Field(..., min_length=1)


class RequisitionResponse(BaseModel):
    id: str
    tenant_id: str
    requisition_number: str
    department_id: Optional[str]
    requested_by_id: str
    required_by_date: date
    status: RequisitionStatus
    estimated_total: Decimal
    justification: Optional[str]
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]
    lines: List[RequisitionLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Purchase Order Schemas
class PurchaseOrderLineCreate(BaseModel):
    item_id: str
    description: str
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    tax_rate_id: Optional[str] = None
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)


class PurchaseOrderLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: str
    description: str
    quantity_ordered: Decimal
    quantity_received: Decimal
    quantity_billed: Decimal
    unit_price: Decimal
    tax_amount: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    vendor_id: str
    requisition_id: Optional[str] = None
    order_date: date
    expected_delivery_date: date
    payment_terms_days: int = Field(default=30, ge=0)
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    lines: List[PurchaseOrderLineCreate] = Field(..., min_length=1)


class PurchaseOrderResponse(BaseModel):
    id: str
    tenant_id: str
    po_number: str
    vendor_id: str
    requisition_id: Optional[str]
    order_date: date
    expected_delivery_date: date
    payment_terms_days: int
    currency: str
    exchange_rate: Decimal
    status: POStatus
    shipping_address: Optional[str]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    approved_by_id: Optional[str]
    approved_at: Optional[datetime]
    notes: Optional[str]
    lines: List[PurchaseOrderLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Goods Receipt Note (GRN) Schemas
class GoodsReceiptLineCreate(BaseModel):
    po_line_id: str
    item_id: str
    quantity_received: Decimal = Field(..., gt=0)
    quantity_accepted: Decimal = Field(..., ge=0)
    quantity_rejected: Decimal = Field(default=Decimal("0.0"), ge=0)
    location_id: str
    lot_number: Optional[str] = None


class GoodsReceiptLineResponse(BaseModel):
    id: str
    po_line_id: str
    item_id: str
    quantity_received: Decimal
    quantity_accepted: Decimal
    quantity_rejected: Decimal
    location_id: str
    lot_number: Optional[str]

    class Config:
        from_attributes = True


class GoodsReceiptNoteCreate(BaseModel):
    po_id: str
    warehouse_id: str
    receipt_date: date
    carrier_tracking_number: Optional[str] = None
    notes: Optional[str] = None
    lines: List[GoodsReceiptLineCreate] = Field(..., min_length=1)


class GoodsReceiptNoteResponse(BaseModel):
    id: str
    tenant_id: str
    grn_number: str
    po_id: str
    vendor_id: str
    warehouse_id: str
    receipt_date: date
    carrier_tracking_number: Optional[str]
    status: GRNStatus
    stock_movement_id: Optional[str]
    notes: Optional[str]
    lines: List[GoodsReceiptLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Vendor Evaluation Schemas
class VendorEvaluationCreate(BaseModel):
    vendor_id: str
    evaluation_date: date
    quality_score: Decimal = Field(..., ge=0, le=100)
    on_time_delivery_score: Decimal = Field(..., ge=0, le=100)
    pricing_score: Decimal = Field(..., ge=0, le=100)
    remarks: Optional[str] = None


class VendorEvaluationResponse(BaseModel):
    id: str
    tenant_id: str
    vendor_id: str
    evaluation_date: date
    quality_score: Decimal
    on_time_delivery_score: Decimal
    pricing_score: Decimal
    overall_rating: Decimal
    evaluator_id: Optional[str]
    remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
