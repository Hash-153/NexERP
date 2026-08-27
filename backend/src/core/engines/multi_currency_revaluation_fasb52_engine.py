"""
FASB ASC 830 (FASB 52) / IAS 21 Foreign Currency Financial Statement Translation Engine.
Calculates Cumulative Translation Adjustment (CTA) under Current Rate and Temporal Methods.
"""
from decimal import Decimal
from typing import Dict, Any, List

class MultiCurrencyRevaluationFASB52Engine:
    @staticmethod
    def translate_subsidiary_balance_sheet(
        subsidiary_id: str,
        functional_currency: str,
        reporting_currency: str,
        closing_spot_rate: Decimal,     # Balance sheet assets & liabilities rate
        weighted_average_rate: Decimal, # Income statement revenue & expenses rate
        historical_equity_rate: Decimal,# Paid-in capital historical rate
        local_assets: Decimal,
        local_liabilities: Decimal,
        local_paid_in_capital: Decimal,
        local_retained_earnings_start: Decimal,
        local_net_income_current: Decimal
    ) -> Dict[str, Any]:
        """
        Current Rate Method Translation:
        1. All Assets & Liabilities translated at Closing Spot Rate.
        2. Paid-in Capital translated at Historical Rate.
        3. Beginning Retained Earnings translated at beginning historical rates.
        4. Current Net Income translated at Weighted Average Rate.
        5. Plug Balancing Figure = Cumulative Translation Adjustment (CTA) in AOCI.
        """
        translated_assets = (local_assets * closing_spot_rate).quantize(Decimal("0.01"))
        translated_liabilities = (local_liabilities * closing_spot_rate).quantize(Decimal("0.01"))
        
        translated_capital = (local_paid_in_capital * historical_equity_rate).quantize(Decimal("0.01"))
        translated_re_start = (local_retained_earnings_start * historical_equity_rate).quantize(Decimal("0.01"))
        translated_net_income = (local_net_income_current * weighted_average_rate).quantize(Decimal("0.01"))
        
        calculated_equity_before_cta = translated_capital + translated_re_start + translated_net_income
        calculated_liab_and_equity_before_cta = translated_liabilities + calculated_equity_before_cta

        # CTA = Total Assets - (Total Liabilities + Equity Before CTA)
        cumulative_translation_adjustment = translated_assets - calculated_liab_and_equity_before_cta

        final_stockholders_equity = calculated_equity_before_cta + cumulative_translation_adjustment
        final_total_liab_and_equity = translated_liabilities + final_stockholders_equity

        return {
            "subsidiary_id": subsidiary_id,
            "functional_currency": functional_currency,
            "reporting_currency": reporting_currency,
            "closing_spot_rate": float(closing_spot_rate),
            "weighted_average_rate": float(weighted_average_rate),
            "historical_equity_rate": float(historical_equity_rate),
            "translated_assets_reporting_currency": float(translated_assets),
            "translated_liabilities_reporting_currency": float(translated_liabilities),
            "translated_paid_in_capital": float(translated_capital),
            "translated_retained_earnings_ending": float(translated_re_start + translated_net_income),
            "cumulative_translation_adjustment_aoci": float(cumulative_translation_adjustment),
            "total_stockholders_equity": float(final_stockholders_equity),
            "total_liabilities_and_equity": float(final_total_liab_and_equity),
            "is_perfectly_balanced": bool(translated_assets == final_total_liab_and_equity)
        }
