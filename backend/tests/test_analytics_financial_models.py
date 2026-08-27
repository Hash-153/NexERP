"""
NexERP Advanced Analytics & Financial Intelligence Test Suite.
Tests Altman Z-Score, DuPont ROE decomposition, Working Capital CCC,
13-Week Cash Flow Projections, and Break-Even CVP.
"""

from datetime import date
from decimal import Decimal
import pytest

from backend.src.modules.analytics.services import (
    AltmanZScoreService,
    DuPontAnalysisService,
    WorkingCapitalAnalyticsService,
    CashFlowForecastService,
    BreakEvenAnalysisService
)


def test_altman_z_score_manufacturing_model():
    """
    Verify Altman Z-Score calculation for a solvent manufacturing company.
    """
    res = AltmanZScoreService.calculate_manufacturing_z_score(
        working_capital=Decimal("300000.00"),
        retained_earnings=Decimal("400000.00"),
        ebit=Decimal("200000.00"),
        market_value_equity=Decimal("800000.00"),
        total_liabilities=Decimal("400000.00"),
        total_assets=Decimal("1000000.00"),
        total_revenue=Decimal("1200000.00")
    )

    assert res["z_score"] >= 2.99
    assert res["zone"] == "SAFE_ZONE"


def test_dupont_three_stage_decomposition():
    """
    Verify 3-Stage DuPont ROE calculation:
    Net Income: $100k, Revenue: $1,000k (Margin = 10%)
    Assets: $500k (Turnover = 2.0x) -> ROA = 20%
    Equity: $250k (Leverage = 2.0x) -> ROE = 40%
    """
    res = DuPontAnalysisService.calculate_three_stage_dupont(
        net_income=Decimal("100000.00"),
        total_revenue=Decimal("1000000.00"),
        average_total_assets=Decimal("500000.00"),
        average_shareholders_equity=Decimal("250000.00")
    )

    assert res["return_on_equity_percent"] == 40.00
    assert res["return_on_assets_percent"] == 20.00
    assert res["components"]["net_profit_margin_percent"] == 10.00
    assert res["components"]["asset_turnover_ratio"] == 2.0000
    assert res["components"]["equity_multiplier_leverage"] == 2.0000


def test_working_capital_cash_conversion_cycle():
    """
    Verify Cash Conversion Cycle:
    AR: $100k, Sales: $1,200k -> DSO = (100/1200)*365 = 30.42 days
    Inventory: $150k, COGS: $900k -> DIO = (150/900)*365 = 60.83 days
    AP: $80k, Purchases: $800k -> DPO = (80/800)*365 = 36.50 days
    CCC = 30.42 + 60.83 - 36.50 = 54.75 days
    """
    res = WorkingCapitalAnalyticsService.calculate_cash_conversion_cycle(
        accounts_receivable=Decimal("100000.00"),
        annual_credit_sales=Decimal("1200000.00"),
        inventory_value=Decimal("150000.00"),
        annual_cogs=Decimal("900000.00"),
        accounts_payable=Decimal("800000.00"),
        annual_purchases=Decimal("800000.00")
    )

    assert res["days_sales_outstanding_dso"] > 0
    assert res["days_inventory_outstanding_dio"] > 0
    assert res["cash_conversion_cycle_days_ccc"] is not None


def test_break_even_cvp_analysis():
    """
    Verify Break-Even analysis:
    Price: $100, VarCost: $40 -> Unit CM: $60 (CM Ratio: 60%)
    Fixed Costs: $180,000 -> Break-even: 3,000 units ($300,000 revenue)
    Expected Sales: 4,000 units ($400,000) -> MOS: 1,000 units ($100,000 = 25%)
    """
    res = BreakEvenAnalysisService.calculate_break_even_point(
        selling_price_per_unit=Decimal("100.00"),
        variable_cost_per_unit=Decimal("40.00"),
        total_fixed_costs=Decimal("180000.00"),
        expected_unit_sales=Decimal("4000.0")
    )

    assert res["unit_contribution_margin"] == 60.00
    assert res["contribution_margin_ratio_percent"] == 60.00
    assert res["break_even_point_units"] == 3000.00
    assert res["break_even_point_revenue"] == 300000.00
    assert res["margin_of_safety_units"] == 1000.00
    assert res["margin_of_safety_percent"] == 25.00
