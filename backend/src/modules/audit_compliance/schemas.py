"""
Audit & Forensic Compliance Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ControlRuleCreate(BaseModel):
    rule_code: str
    rule_name: str
    description: str
    threshold_amount: Decimal = Decimal("100000.00")

class AnomalyDetectionRequest(BaseModel):
    entity_name: str
    posted_amount: Decimal
    is_weekend: bool = False
    is_round_number: bool = False
    is_manual_entry: bool = True
