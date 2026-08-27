"""
Subscription Billing Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SubscriptionCreate(BaseModel):
    customer_account_id: str
    plan_name: str
    billing_frequency: str = "ANNUAL_UPFRONT"
    contract_start_date: date
    contract_end_date: date
    annual_contract_value: Decimal
    seat_count: int = 100
