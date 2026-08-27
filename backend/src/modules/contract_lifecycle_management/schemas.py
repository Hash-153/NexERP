"""
Contract Lifecycle Management Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class MilestoneInput(BaseModel):
    milestone_name: str
    milestone_percentage: Decimal
    billing_amount: Decimal
    target_delivery_date: date

class ContractDocumentCreate(BaseModel):
    contract_number: str
    title: str
    contract_type: str = "MASTER_SERVICES_AGREEMENT"
    counterparty_name: str
    counterparty_signatory_email: str
    effective_date: date
    expiration_date: date
    renewal_type: str = "EVERGREEN_AUTO_RENEW"
    renewal_notice_days: int = 60
    total_contract_value: Decimal
    governing_law_jurisdiction: str = "Delaware, USA"
    milestones: List[MilestoneInput] = []

class ContractDocumentResponse(BaseModel):
    id: str
    tenant_id: str
    contract_number: str
    title: str
    status: str
    counterparty_name: str
    effective_date: date
    expiration_date: date
    total_contract_value: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
