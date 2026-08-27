"""
NexERP Sales Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field
from .enums import LeadStage, QuoteStatus, SalesOrderStatus, DeliveryStatus


# Lead Schemas
class LeadBase(BaseModel):
    contact_name: str = Field(..., min_length=2, max_length=150)
    company_name: str = Field(..., min_length=2, max_length=150)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    stage: LeadStage = LeadStage.NEW
    estimated_value: Decimal = Field(default=Decimal("0.0"), ge=0)
    win_probability_percent: int = Field(default=20, ge=0, le=100)
    assigned_sales_rep_id: Optional[str] = None
    source: str = "Website"
    notes: Optional[str] = None


class LeadCreate(LeadBase):
    pass


class LeadResponse(LeadBase):
    id: str
    tenant_id: str
    lead_number: str
    created_at: datetime

    class Config:
        from_attributes = True


# Sales Quotation Schemas
class SalesQuotationLineCreate(BaseModel):
    item_id: str
    description: str
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)


class SalesQuotationLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: str
    description: str
    quantity: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    tax_amount: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True


class SalesQuotationCreate(BaseModel):
    customer_id: str
    lead_id: Optional[str] = None
    quote_date: date
    expiry_date: date
    currency: str = "USD"
    terms_and_conditions: Optional[str] = None
    lines: List[SalesQuotationLineCreate] = Field(..., min_length=1)


class SalesQuotationResponse(BaseModel):
    id: str
    tenant_id: str
    quote_number: str
    customer_id: str
    lead_id: Optional[str]
    quote_date: date
    expiry_date: date
    status: QuoteStatus
    currency: str
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    terms_and_conditions: Optional[str]
    lines: List[SalesQuotationLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Sales Order Schemas
class SalesOrderLineCreate(BaseModel):
    item_id: str
    description: str
    quantity_ordered: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    discount_percent: Decimal = Field(default=Decimal("0.0"), ge=0, le=100)
    tax_rate_id: Optional[str] = None
    tax_amount: Decimal = Field(default=Decimal("0.0"), ge=0)


class SalesOrderLineResponse(BaseModel):
    id: str
    line_number: int
    item_id: str
    description: str
    quantity_ordered: Decimal
    quantity_allocated: Decimal
    quantity_fulfilled: Decimal
    quantity_invoiced: Decimal
    unit_price: Decimal
    discount_percent: Decimal
    tax_amount: Decimal
    line_total: Decimal

    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    customer_id: str
    quotation_id: Optional[str] = None
    order_date: date
    requested_delivery_date: date
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    shipping_address: Optional[str] = None
    payment_terms_days: int = Field(default=30, ge=0)
    notes: Optional[str] = None
    lines: List[SalesOrderLineCreate] = Field(..., min_length=1)


class SalesOrderResponse(BaseModel):
    id: str
    tenant_id: str
    so_number: str
    customer_id: str
    quotation_id: Optional[str]
    order_date: date
    requested_delivery_date: date
    currency: str
    exchange_rate: Decimal
    status: SalesOrderStatus
    shipping_address: Optional[str]
    payment_terms_days: int
    subtotal: Decimal
    discount_amount: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    notes: Optional[str]
    lines: List[SalesOrderLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Fulfillment Delivery Schemas
class FulfillmentDeliveryLineCreate(BaseModel):
    so_line_id: str
    item_id: str
    location_id: str
    quantity_shipped: Decimal = Field(..., gt=0)


class FulfillmentDeliveryLineResponse(BaseModel):
    id: str
    so_line_id: str
    item_id: str
    location_id: str
    quantity_shipped: Decimal

    class Config:
        from_attributes = True


class FulfillmentDeliveryCreate(BaseModel):
    sales_order_id: str
    warehouse_id: str
    dispatch_date: date
    carrier: str = "FedEx Ground"
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    lines: List[FulfillmentDeliveryLineCreate] = Field(..., min_length=1)


class FulfillmentDeliveryResponse(BaseModel):
    id: str
    tenant_id: str
    delivery_number: str
    sales_order_id: str
    customer_id: str
    warehouse_id: str
    dispatch_date: date
    carrier: str
    tracking_number: Optional[str]
    status: DeliveryStatus
    stock_movement_id: Optional[str]
    notes: Optional[str]
    lines: List[FulfillmentDeliveryLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
