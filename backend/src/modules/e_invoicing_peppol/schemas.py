"""
Global E-Invoicing Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class EInvoiceGenerateRequest(BaseModel):
    invoice_id: str
    invoice_number: str
    issue_date: date
    due_date: date
    seller_vat_id: str
    buyer_vat_id: str
    buyer_endpoint_scheme: str = "0088"
    buyer_endpoint_id: str
    currency: str = "EUR"
    total_amount: Decimal
    tax_amount: Decimal
    standard: str = "PEPPOL_BIS_BILLING_3"

class EInvoiceResponse(BaseModel):
    id: str
    invoice_number: str
    standard: str
    transmission_status: str
    tax_authority_uuid: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
