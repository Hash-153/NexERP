"""
Capital Expenditure (CAPEX) Discounted Cash Flow (DCF), NPV, IRR, and Payback Valuation Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List

class CapexDCFEvaluationService:
    @staticmethod
    def calculate_npv(discount_rate: Decimal, initial_outlay: Decimal, annual_cash_flows: List[Decimal]) -> Decimal:
        npv = -initial_outlay
        for year, cf in enumerate(annual_cash_flows, start=1):
            discount_factor = (Decimal("1.0") + discount_rate) ** year
            npv += cf / discount_factor
        return npv.quantize(Decimal("0.01"))

    @classmethod
    def evaluate_capex_project(
        cls,
        project_name: str,
        initial_capex_outlay: Decimal,
        annual_cash_flows: List[Decimal],
        hurdle_rate: Decimal = Decimal("0.10")  # 10% WACC
    ) -> Dict[str, Any]:
        npv = cls.calculate_npv(hurdle_rate, initial_capex_outlay, annual_cash_flows)
        
        # Calculate Payback Period
        cumulative = Decimal("0.0")
        payback_years = Decimal("0.0")
        for yr, cf in enumerate(annual_cash_flows, start=1):
            cumulative += cf
            if cumulative >= initial_capex_outlay:
                overshoot = cumulative - initial_capex_outlay
                fraction = Decimal("1.0") - (overshoot / cf) if cf > 0 else Decimal("0.0")
                payback_years = Decimal(str(yr - 1)) + fraction
                break

        # Approximate IRR using bisection
        low_rate = Decimal("0.0")
        high_rate = Decimal("1.0")
        irr = Decimal("0.0")
        for _ in range(50):
            mid_rate = (low_rate + high_rate) / Decimal("2.0")
            mid_npv = cls.calculate_npv(mid_rate, initial_capex_outlay, annual_cash_flows)
            if abs(mid_npv) < Decimal("1.00"):
                irr = mid_rate
                break
            if mid_npv > 0:
                low_rate = mid_rate
            else:
                high_rate = mid_rate
            irr = mid_rate

        profitability_index = ((npv + initial_capex_outlay) / initial_capex_outlay).quantize(Decimal("0.01")) if initial_capex_outlay > 0 else Decimal("0.0")

        return {
            "project_name": project_name,
            "initial_outlay": float(initial_capex_outlay),
            "hurdle_rate_wacc": float(hurdle_rate),
            "net_present_value_npv": float(npv),
            "internal_rate_of_return_irr": float((irr * Decimal("100.0")).quantize(Decimal("0.01"))),
            "payback_period_years": float(payback_years.quantize(Decimal("0.01"))),
            "profitability_index": float(profitability_index),
            "recommendation": "APPROVE_CAPEX" if npv > 0 and irr >= hurdle_rate else "REJECT_SUB_HURDLE"
        }
