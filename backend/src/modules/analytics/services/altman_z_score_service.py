"""
NexERP Altman Z-Score Corporate Financial Distress & Bankruptcy Prediction Engine.
Implements Edward Altman's Z-Score models:
1. Original Manufacturing Model (1968):
   Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 0.999*X5
   - Safe Zone: Z > 2.99
   - Grey Zone: 1.81 <= Z <= 2.99
   - Distress Zone: Z < 1.81

2. Revised Non-Manufacturing / Emerging Markets Model (Altman Z'-Score):
   Z' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
   - Safe Zone: Z' > 2.60
   - Grey Zone: 1.10 <= Z' <= 2.60
   - Distress Zone: Z' < 1.10
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional


class AltmanZScoreService:
    """
    Altman Z-Score Credit Risk & Solvency Evaluation Service.
    """

    @classmethod
    def calculate_manufacturing_z_score(
        cls,
        working_capital: Decimal,
        retained_earnings: Decimal,
        ebit: Decimal,
        market_value_equity: Decimal,
        total_liabilities: Decimal,
        total_assets: Decimal,
        total_revenue: Decimal
    ) -> Dict:
        """
        Compute classic Altman Z-Score for manufacturing companies.
        """
        if total_assets <= Decimal("0.0") or total_liabilities <= Decimal("0.0"):
            raise ValueError("Total Assets and Total Liabilities must be strictly positive.")

        # X1 = Working Capital / Total Assets (Liquidity ratio)
        x1 = (working_capital / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        # X2 = Retained Earnings / Total Assets (Cumulative profitability)
        x2 = (retained_earnings / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        # X3 = EBIT / Total Assets (Productivity of assets / ROA)
        x3 = (ebit / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        # X4 = Market/Book Value Equity / Total Liabilities (Solvency/Leverage)
        x4 = (market_value_equity / total_liabilities).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        # X5 = Sales / Total Assets (Asset Turnover)
        x5 = (total_revenue / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        z_score = (
            (Decimal("1.2") * x1) +
            (Decimal("1.4") * x2) +
            (Decimal("3.3") * x3) +
            (Decimal("0.6") * x4) +
            (Decimal("0.999") * x5)
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        if z_score >= Decimal("2.99"):
            zone = "SAFE_ZONE"
            risk_description = "Low probability of financial distress within 24 months."
        elif z_score >= Decimal("1.81"):
            zone = "GREY_ZONE"
            risk_description = "Moderate risk of financial distress. Close monitoring recommended."
        else:
            zone = "DISTRESS_ZONE"
            risk_description = "High probability of bankruptcy/insolvency within 24 months."

        return {
            "model_type": "ALTMAN_MANUFACTURING_1968",
            "z_score": float(z_score),
            "zone": zone,
            "risk_assessment": risk_description,
            "ratios": {
                "x1_working_capital_to_assets": float(x1),
                "x2_retained_earnings_to_assets": float(x2),
                "x3_ebit_to_assets": float(x3),
                "x4_equity_to_liabilities": float(x4),
                "x5_asset_turnover": float(x5)
            }
        }

    @classmethod
    def calculate_non_manufacturing_z_score(
        cls,
        working_capital: Decimal,
        retained_earnings: Decimal,
        ebit: Decimal,
        book_value_equity: Decimal,
        total_liabilities: Decimal,
        total_assets: Decimal
    ) -> Dict:
        """
        Compute Altman Z''-Score for non-manufacturing and service sector firms.
        """
        if total_assets <= Decimal("0.0") or total_liabilities <= Decimal("0.0"):
            raise ValueError("Total Assets and Total Liabilities must be strictly positive.")

        x1 = (working_capital / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        x2 = (retained_earnings / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        x3 = (ebit / total_assets).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        x4 = (book_value_equity / total_liabilities).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        z_prime = (
            (Decimal("6.56") * x1) +
            (Decimal("3.26") * x2) +
            (Decimal("6.72") * x3) +
            (Decimal("1.05") * x4)
        ).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

        if z_prime >= Decimal("2.60"):
            zone = "SAFE_ZONE"
            risk_description = "Solid financial health and robust solvency."
        elif z_prime >= Decimal("1.10"):
            zone = "GREY_ZONE"
            risk_description = "Cautionary financial condition."
        else:
            zone = "DISTRESS_ZONE"
            risk_description = "Serious insolvency distress vulnerability."

        return {
            "model_type": "ALTMAN_REVISED_NON_MANUFACTURING",
            "z_prime_score": float(z_prime),
            "zone": zone,
            "risk_assessment": risk_description,
            "ratios": {
                "x1_working_capital_to_assets": float(x1),
                "x2_retained_earnings_to_assets": float(x2),
                "x3_ebit_to_assets": float(x3),
                "x4_book_equity_to_liabilities": float(x4)
            }
        }
