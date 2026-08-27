"""
Vendor Collaboration Portal Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class ASNSubmissionCreate(BaseModel):
    vendor_id: str
    purchase_order_id: str
    asn_number: str
    sscc_barcode: str
    shipped_date: datetime
    estimated_dock_arrival: datetime
    carrier_tracking_number: Optional[str] = None
    total_cartons: int = 1
    total_shipped_qty: Decimal

class VendorInvoiceSubmitRequest(BaseModel):
    vendor_id: str
    purchase_order_id: str
    invoice_number: str
    invoice_date: date
    due_date: date
    currency: str = "USD"
    subtotal_amount: Decimal
    tax_amount: Decimal = Decimal("0.0")
