"""
NexERP Executive Analytics & BI Dashboard Schemas.
"""

from typing import List, Optional
from datetime import date
from decimal import Decimal
from pydantic import BaseModel


class ExecutiveDashboardKPIs(BaseModel):
    total_revenue_ytd: Decimal
    gross_margin_percentage: Decimal
    cash_and_bank_balance: Decimal
    accounts_receivable_outstanding: Decimal
    accounts_payable_outstanding: Decimal
    total_inventory_valuation: Decimal
    open_sales_orders_value: Decimal
    open_production_orders_count: int
    active_employees_count: int


class RevenueTrendPoint(BaseModel):
    month_name: str
    revenue: Decimal
    cost_of_goods_sold: Decimal
    net_profit: Decimal


class ExecutiveDashboardResponse(BaseModel):
    as_of_date: date
    kpis: ExecutiveDashboardKPIs
    revenue_trends: List[RevenueTrendPoint] = []
    top_selling_items: List[dict] = []
    cash_flow_summary: dict = {}
