"""
NexERP Accounts Receivable Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from .enums import InvoiceStatus, ReceiptStatus, DunningLevel


# Customer Schemas
class CustomerBase(BaseModel):
    customer_number: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    tax_identifier: Optional[str] = None
    customer_group: str = "Commercial"
    payment_terms_days: int = Field(default=30, ge=0)
    credit_limit: Decimal = Field(default=Decimal("50000.0"), ge=0)
    credit_hold: bool = False
    currency: str = "USD"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    ar_account_id: Optional[str] = None
    revenue_account_id: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    tax_identifier: Optional[str] = None
    customer_group: Optional[str] = None
    payment_terms_days: Optional[int] = None
    credit_limit: Optional[Decimal] = None
    credit_hold: Optional[bool] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    billing_address: Optional[str] = None
    shipping_address: Optional[str] = None
    ar_account_id: Optional[str] = None
    revenue_account_id: Optional[str] = None


class CustomerResponse(CustomerBase):
    id: str
    tenant_id: str
    current_balance: Decimal
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Sales Invoice Schemas
class SalesInvoiceLineCreate(BaseModel):
    item_id: Optional[str] = None
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    tax_rate_id: Optional[str] = None
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    revenue_account_id: str
    cost_center_id: Optional[str] = None
    project_id: Optional[str] = None


class SalesInvoiceLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: Optional[str]
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    tax_amount: Decimal
    line_total: Decimal
    revenue_account_id: str
    cost_center_id: Optional[str]
    project_id: Optional[str]

    class Config:
        from_attributes = True


class SalesInvoiceCreate(BaseModel):
    customer_id: str
    invoice_date: date
    due_date: date
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    sales_order_id: Optional[str] = None
    fulfillment_delivery_id: Optional[str] = None
    notes: Optional[str] = None
    lines: List[SalesInvoiceLineCreate] = Field(..., min_length=1)


class SalesInvoiceResponse(BaseModel):
    id: str
    tenant_id: str
    invoice_number: str
    customer_id: str
    invoice_date: date
    due_date: date
    currency: str
    exchange_rate: Decimal
    status: InvoiceStatus
    sales_order_id: Optional[str]
    fulfillment_delivery_id: Optional[str]
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_due: Decimal
    dunning_level: int
    journal_entry_id: Optional[str]
    notes: Optional[str]
    lines: List[SalesInvoiceLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Payment Receipt Schemas
class ReceiptAllocationCreate(BaseModel):
    invoice_id: str
    allocated_amount: Decimal = Field(..., gt=0)
    early_discount_taken: Decimal = Decimal("0.0")


class PaymentReceiptCreate(BaseModel):
    customer_id: str
    receipt_date: date
    bank_account_id: str
    payment_method: str = "WIRE_TRANSFER"
    total_amount: Decimal = Field(..., gt=0)
    allocations: List[ReceiptAllocationCreate] = []
    notes: Optional[str] = None


class ReceiptAllocationResponse(BaseModel):
    id: str
    invoice_id: str
    allocated_amount: Decimal
    early_discount_taken: Decimal

    class Config:
        from_attributes = True


class PaymentReceiptResponse(BaseModel):
    id: str
    tenant_id: str
    receipt_number: str
    customer_id: str
    receipt_date: date
    bank_account_id: str
    payment_method: str
    total_amount: Decimal
    unallocated_amount: Decimal
    status: ReceiptStatus
    journal_entry_id: Optional[str]
    allocations: List[ReceiptAllocationResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# AR Aging Schemas
class ARAgingBucket(BaseModel):
    customer_id: str
    customer_name: str
    customer_number: str
    current: Decimal
    days_1_30: Decimal
    days_31_60: Decimal
    days_61_90: Decimal
    days_90_plus: Decimal
    total_outstanding: Decimal


class ARAgingReportResponse(BaseModel):
    as_of_date: date
    customers: List[ARAgingBucket]
    total_current: Decimal
    total_1_30: Decimal
    total_31_60: Decimal
    total_61_90: Decimal
    total_90_plus: Decimal
    grand_total: Decimal
    dso_days: float
