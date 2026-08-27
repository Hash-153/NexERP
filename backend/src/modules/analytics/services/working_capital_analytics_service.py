"""
NexERP Working Capital & Cash Conversion Cycle (CCC) Analytical Engine.
Calculates:
- Days Sales Outstanding (DSO) = (AR / Credit Sales) * 365
- Days Inventory Outstanding (DIO) = (Ending Inventory / COGS) * 365
- Days Payable Outstanding (DPO) = (AP / Total Purchases or COGS) * 365
- Cash Conversion Cycle (CCC) = DSO + DIO - DPO
- Working Capital Ratios: Current Ratio, Quick Ratio (Acid-Test), Cash Ratio.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict


class WorkingCapitalAnalyticsService:
    """
    Working Capital Efficiency & Liquidity Ratios Engine.
    """

    @classmethod
    def calculate_cash_conversion_cycle(
        cls,
        accounts_receivable: Decimal,
        annual_credit_sales: Decimal,
        inventory_value: Decimal,
        annual_cogs: Decimal,
        accounts_payable: Decimal,
        annual_purchases: Decimal,
        days_in_period: int = 365
    ) -> Dict:
        """
        Compute Days Sales Outstanding (DSO), Days Inventory Outstanding (DIO),
        Days Payable Outstanding (DPO), and Net Cash Conversion Cycle (CCC).
        """
        period_days = Decimal(str(days_in_period))

        dso = ((accounts_receivable / annual_credit_sales) * period_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if annual_credit_sales > Decimal("0.0") else Decimal("0.0")
        dio = ((inventory_value / annual_cogs) * period_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if annual_cogs > Decimal("0.0") else Decimal("0.0")
        dpo = ((accounts_payable / annual_purchases) * period_days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if annual_purchases > Decimal("0.0") else Decimal("0.0")

        ccc = (dso + dio - dpo).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "days_sales_outstanding_dso": float(dso),
            "days_inventory_outstanding_dio": float(dio),
            "days_payable_outstanding_dpo": float(dpo),
            "cash_conversion_cycle_days_ccc": float(ccc),
            "efficiency_assessment": "HIGHLY_EFFICIENT" if ccc < Decimal("30.0") else ("MODERATE" if ccc < Decimal("75.0") else "WORKING_CAPITAL_TIED_UP")
        }

    @classmethod
    def calculate_liquidity_ratios(
        cls,
        cash_and_equivalents: Decimal,
        marketable_securities: Decimal,
        accounts_receivable: Decimal,
        inventory: Decimal,
        prepaid_expenses: Decimal,
        current_liabilities: Decimal
    ) -> Dict:
        """
        Compute standard corporate liquidity & solvency ratios.
        """
        if current_liabilities <= Decimal("0.0"):
            raise ValueError("Current liabilities must be greater than zero.")

        total_current_assets = cash_and_equivalents + marketable_securities + accounts_receivable + inventory + prepaid_expenses
        quick_assets = cash_and_equivalents + marketable_securities + accounts_receivable
        cash_assets = cash_and_equivalents + marketable_securities

        current_ratio = (total_current_assets / current_liabilities).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        quick_ratio = (quick_assets / current_liabilities).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        cash_ratio = (cash_assets / current_liabilities).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net_working_capital = total_current_assets - current_liabilities

        return {
            "total_current_assets": float(total_current_assets),
            "current_liabilities": float(current_liabilities),
            "net_working_capital": float(net_working_capital),
            "current_ratio": float(current_ratio),
            "quick_ratio_acid_test": float(quick_ratio),
            "cash_ratio": float(cash_ratio),
            "liquidity_health": "STRONG" if quick_ratio >= Decimal("1.0") and current_ratio >= Decimal("1.5") else "VULNERABLE"
        }
