"""
NexERP DuPont ROE Decomposition Financial Analysis Engine.
Calculates 3-Stage and 5-Stage DuPont identity models:
- 3-Stage: Net Profit Margin x Asset Turnover x Financial Leverage Multiplier
- 5-Stage: Tax Burden x Interest Burden x Operating Margin x Asset Turnover x Financial Leverage
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class DuPontAnalysisService:
    """
    DuPont Return on Equity (ROE) Analytical Engine.
    """

    @classmethod
    def calculate_three_stage_dupont(
        cls,
        net_income: Decimal,
        total_revenue: Decimal,
        average_total_assets: Decimal,
        average_shareholders_equity: Decimal
    ) -> Dict:
        """
        Compute 3-Stage DuPont ROE Decomposition.
        """
        if total_revenue <= Decimal("0.0") or average_total_assets <= Decimal("0.0") or average_shareholders_equity <= Decimal("0.0"):
            raise ValueError("Revenue, Average Assets, and Average Equity must be strictly positive.")

        # 1. Net Profit Margin = Net Income / Revenue
        profit_margin = ((net_income / total_revenue) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # 2. Asset Turnover = Revenue / Assets
        asset_turnover = (total_revenue / average_total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        # 3. Equity Multiplier (Financial Leverage) = Assets / Equity
        equity_multiplier = (average_total_assets / average_shareholders_equity).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        # Return on Assets (ROA) = Profit Margin * Asset Turnover
        roa = ((net_income / average_total_assets) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        # Return on Equity (ROE) = ROA * Equity Multiplier
        roe = ((net_income / average_shareholders_equity) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "model": "DUPONT_THREE_STAGE",
            "return_on_equity_percent": float(roe),
            "return_on_assets_percent": float(roa),
            "components": {
                "net_profit_margin_percent": float(profit_margin),
                "asset_turnover_ratio": float(asset_turnover),
                "equity_multiplier_leverage": float(equity_multiplier)
            }
        }

    @classmethod
    def calculate_five_stage_dupont(
        cls,
        net_income: Decimal,
        ebt: Decimal,
        ebit: Decimal,
        total_revenue: Decimal,
        average_total_assets: Decimal,
        average_shareholders_equity: Decimal
    ) -> Dict:
        """
        Compute 5-Stage DuPont ROE Decomposition isolating Tax Burden, Interest Burden, and Operating Efficiency.
        """
        if ebt <= Decimal("0.0") or ebit <= Decimal("0.0") or total_revenue <= Decimal("0.0") or average_total_assets <= Decimal("0.0") or average_shareholders_equity <= Decimal("0.0"):
            raise ValueError("All denominator parameters must be positive non-zero amounts.")

        tax_burden = (net_income / ebt).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        interest_burden = (ebt / ebit).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        operating_margin = ((ebit / total_revenue) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        asset_turnover = (total_revenue / average_total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        equity_multiplier = (average_total_assets / average_shareholders_equity).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        roe = ((net_income / average_shareholders_equity) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "model": "DUPONT_FIVE_STAGE",
            "return_on_equity_percent": float(roe),
            "components": {
                "tax_burden_ratio": float(tax_burden),
                "interest_burden_ratio": float(interest_burden),
                "operating_profit_margin_percent": float(operating_margin),
                "asset_turnover_ratio": float(asset_turnover),
                "equity_multiplier_leverage": float(equity_multiplier)
            }
        }
