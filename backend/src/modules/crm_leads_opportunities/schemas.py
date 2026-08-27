"""
CRM & CPQ Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CRMLeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    company_name: str
    job_title: Optional[str] = None
    lead_source: str = "ORGANIC_WEB"
    budget_amount: Optional[Decimal] = None
    decision_timeframe_months: int = 3
    notes: Optional[str] = None

class CRMLeadResponse(CRMLeadCreate):
    id: str
    tenant_id: str
    qualification_status: str
    predictive_score: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CRMOpportunityCreate(BaseModel):
    opportunity_name: str
    account_id: str
    deal_value: Decimal
    stage: str = "PROSPECTING"
    expected_close_date: date
    assigned_sales_rep_id: str
    lead_source: str = "ORGANIC_WEB"

class CPQQuoteLineInput(BaseModel):
    item_id: str
    product_name: str
    quantity: Decimal
    list_unit_price: Decimal
    unit_cost: Decimal = Decimal("0.0")
    discount_percentage: Decimal = Decimal("0.0")

class CPQQuoteCreate(BaseModel):
    opportunity_id: str
    quote_number: str
    valid_until_date: date
    lines: List[CPQQuoteLineInput]
