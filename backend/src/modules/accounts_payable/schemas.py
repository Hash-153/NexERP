"""
NexERP Accounts Payable Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from .enums import BillStatus, PaymentMethod, PaymentRunStatus


# Vendor Schemas
class VendorBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    tax_identifier: Optional[str] = None
    payment_terms_days: int = Field(default=30, ge=0)
    credit_limit: Decimal = Field(default=Decimal("0.0"), ge=0)
    currency: str = "USD"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bank_account_details: Optional[str] = None
    ap_account_id: Optional[str] = None
    expense_account_id: Optional[str] = None
    is_1099_eligible: bool = False


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    tax_identifier: Optional[str] = None
    payment_terms_days: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    bank_account_details: Optional[str] = None
    ap_account_id: Optional[str] = None
    expense_account_id: Optional[str] = None
    is_1099_eligible: Optional[bool] = None


class VendorResponse(VendorBase):
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Vendor Bill Schemas
class VendorBillLineCreate(BaseModel):
    item_id: Optional[str] = None
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    tax_rate_id: Optional[str] = None
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    expense_account_id: str
    cost_center_id: Optional[str] = None
    project_id: Optional[str] = None


class VendorBillLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: Optional[str]
    description: str
    quantity: Decimal
    unit_price: Decimal
    tax_amount: Decimal
    line_total: Decimal
    expense_account_id: str
    cost_center_id: Optional[str]
    project_id: Optional[str]

    class Config:
        from_attributes = True


class VendorBillCreate(BaseModel):
    bill_number: str
    vendor_id: str
    bill_date: date
    due_date: date
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    purchase_order_id: Optional[str] = None
    goods_receipt_id: Optional[str] = None
    notes: Optional[str] = None
    lines: List[VendorBillLineCreate] = Field(..., min_length=1)


class VendorBillResponse(BaseModel):
    id: str
    tenant_id: str
    bill_number: str
    system_reference: str
    vendor_id: str
    bill_date: date
    due_date: date
    currency: str
    exchange_rate: Decimal
    status: BillStatus
    purchase_order_id: Optional[str]
    goods_receipt_id: Optional[str]
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    journal_entry_id: Optional[str]
    notes: Optional[str]
    lines: List[VendorBillLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# 3-Way Match Schemas
class ThreeWayMatchResponse(BaseModel):
    id: str
    bill_id: str
    purchase_order_id: Optional[str]
    goods_receipt_id: Optional[str]
    is_matched: bool
    price_variance_percent: Decimal
    quantity_variance_percent: Decimal
    tolerance_exceeded: bool
    matched_at: datetime
    details: Optional[dict]

    class Config:
        from_attributes = True


# Payment Run Schemas
class PaymentRunItemCreate(BaseModel):
    bill_id: str
    payment_amount: Decimal = Field(..., gt=0)
    early_discount_captured: Decimal = Decimal("0.0")


class PaymentRunCreate(BaseModel):
    run_date: date
    bank_account_id: str
    payment_method: PaymentMethod = PaymentMethod.WIRE_TRANSFER
    notes: Optional[str] = None
    items: List[PaymentRunItemCreate] = Field(..., min_length=1)


class PaymentRunItemResponse(BaseModel):
    id: str
    bill_id: str
    payment_amount: Decimal
    early_discount_captured: Decimal

    class Config:
        from_attributes = True


class PaymentRunResponse(BaseModel):
    id: str
    tenant_id: str
    run_number: str
    run_date: date
    bank_account_id: str
    payment_method: PaymentMethod
    total_amount: Decimal
    status: PaymentRunStatus
    journal_entry_id: Optional[str]
    items: List[PaymentRunItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# AP Aging Schemas
class APAgingBucket(BaseModel):
    vendor_id: str
    vendor_name: str
    vendor_code: str
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_90_plus: Decimal
    total_outstanding: Decimal


class APAgingReportResponse(BaseModel):
    as_of_date: date
    vendors: List[APAgingBucket]
    total_current: Decimal
    total_1_30: Decimal
    total_31_60: Decimal
    total_61_90: Decimal
    total_90_plus: Decimal
    grand_total: Decimal
