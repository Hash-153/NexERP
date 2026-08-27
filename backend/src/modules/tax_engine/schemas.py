"""
Tax Engine Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class TaxCalculationRequest(BaseModel):
    transaction_id: str
    country_code: str = "US"
    state_province: str
    postal_code: str
    line_amount: Decimal
    is_resale_exempt: bool = False
    tax_code: str = "DEFAULT_TAXABLE"

class TaxCalculationResult(BaseModel):
    transaction_id: str
    taxable_amount: Decimal
    combined_rate: Decimal
    state_tax_amount: Decimal
    local_tax_amount: Decimal
    total_tax_amount: Decimal
    jurisdiction_summary: str
