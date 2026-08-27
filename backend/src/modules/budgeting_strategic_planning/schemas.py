"""
Strategic Budgeting Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CostCenterLineInput(BaseModel):
    cost_center_code: str
    cost_center_name: str
    expense_type: str
    monthly_uniform_amount: Decimal

class StrategicBudgetPlanCreate(BaseModel):
    fiscal_year: int
    plan_name: str
    version_type: str = "ORIGINAL_APPROVED"
    total_revenue_budget: Decimal
    total_capex_budget: Decimal
    cost_centers: List[CostCenterLineInput] = []

class StrategicBudgetPlanResponse(BaseModel):
    id: str
    tenant_id: str
    fiscal_year: int
    plan_name: str
    status: str
    total_revenue_budget: Decimal
    total_opex_budget: Decimal
    net_ebitda_budget: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
