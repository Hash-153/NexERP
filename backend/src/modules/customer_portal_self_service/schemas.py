"""
Customer Portal Pydantic Schemas.
"""
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class SupportTicketCreate(BaseModel):
    customer_account_id: str
    contact_email: str
    subject: str
    description: str
    severity: str = "SEV_3_MEDIUM_INQUIRY"

class RMARequestCreate(BaseModel):
    customer_account_id: str
    original_sales_order_id: str
    item_id: str
    quantity_to_return: Decimal
    return_reason: str
