"""
NexERP Fixed Asset Impairment & Disposal Accounting Engine (IAS 36 / US GAAP ASC 360).
Performs:
- Carrying Value vs Recoverable Amount testing
- Value in Use (DCF - Discounted Cash Flow) and Fair Value Less Costs of Disposal (FVLCD)
- Impairment Loss calculation and GL journal voucher creation
- Asset Scrap / Sale Disposal Gain/Loss calculations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class AssetImpairmentService:
    """
    IAS 36 Fixed Asset Impairment & PPE Disposal Service.
    """

    @classmethod
    def evaluate_impairment(
        cls,
        carrying_book_value: Decimal,
        fair_value_less_costs_to_sell: Decimal,
        discounted_value_in_use: Decimal
    ) -> Dict:
        """
        Recoverable Amount = Max(Fair Value Less Costs to Sell, Value in Use).
        If Carrying Book Value > Recoverable Amount -> Impairment Loss = Carrying Value - Recoverable Amount.
        """
        recoverable_amount = max(fair_value_less_costs_to_sell, discounted_value_in_use)
        impairment_loss = max(Decimal("0.0"), carrying_book_value - recoverable_amount)
        new_carrying_value = carrying_book_value - impairment_loss

        return {
            "carrying_book_value": float(carrying_book_value),
            "fair_value_less_costs_to_sell": float(fair_value_less_costs_to_sell),
            "discounted_value_in_use": float(discounted_value_in_use),
            "recoverable_amount": float(recoverable_amount),
            "is_impaired": impairment_loss > Decimal("0.0"),
            "impairment_loss_amount": float(impairment_loss),
            "adjusted_carrying_value": float(new_carrying_value),
            "accounting_entry": {
                "debit_account": "Impairment Loss Expense (P&L)",
                "credit_account": "Accumulated Impairment / PPE Asset",
                "amount": float(impairment_loss)
            } if impairment_loss > Decimal("0.0") else None
        }

    @classmethod
    def calculate_asset_disposal_gain_loss(
        cls,
        acquisition_cost: Decimal,
        accumulated_depreciation: Decimal,
        proceeds_from_sale: Decimal,
        disposal_costs: Decimal = Decimal("0.0")
    ) -> Dict:
        """
        Compute net gain or loss on sale/disposal of capitalized asset.
        Net Book Value = Acquisition Cost - Accumulated Depreciation.
        Net Proceeds = Sale Proceeds - Disposal Costs.
        Gain/(Loss) = Net Proceeds - Net Book Value.
        """
        net_book_value = acquisition_cost - accumulated_depreciation
        net_proceeds = proceeds_from_sale - disposal_costs
        gain_loss = net_proceeds - net_book_value

        return {
            "acquisition_cost": float(acquisition_cost),
            "accumulated_depreciation": float(accumulated_depreciation),
            "net_book_value": float(net_book_value),
            "gross_sale_proceeds": float(proceeds_from_sale),
            "disposal_costs": float(disposal_costs),
            "net_proceeds": float(net_proceeds),
            "gain_or_loss_amount": float(gain_loss),
            "disposal_result": "GAIN_ON_DISPOSAL" if gain_loss >= Decimal("0.0") else "LOSS_ON_DISPOSAL"
        }
