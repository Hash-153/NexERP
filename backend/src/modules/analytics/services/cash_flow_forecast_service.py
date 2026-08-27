"""
NexERP 13-Week Rolling Direct Cash Flow Projection Engine.
Aggregates known future cash outflows (Vendor Bills AP, Payroll runs, Tax filings, Debt service)
and modeled inflows (Customer Invoices AR collection curves, POS sales) to predict net treasury positions.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class CashFlowForecastService:
    """
    13-Week Direct Cash Flow Rolling Projection Service.
    """

    @classmethod
    def generate_thirteen_week_projection(
        cls,
        starting_cash_balance: Decimal,
        start_date: date,
        expected_weekly_inflows: List[Decimal],
        expected_weekly_ap_disbursements: List[Decimal],
        expected_weekly_payroll: List[Decimal],
        other_weekly_outflows: Optional[List[Decimal]] = None
    ) -> Dict:
        """
        Generate week-by-week cash balance projection for 13 weeks.
        """
        weeks_count = 13
        other_outflows = other_weekly_outflows or [Decimal("0.0")] * weeks_count

        projection_schedule = []
        running_cash = starting_cash_balance
        min_projected_cash = starting_cash_balance
        lowest_cash_week = 1

        for w_idx in range(weeks_count):
            week_start = start_date + timedelta(days=w_idx * 7)
            inflows = expected_weekly_inflows[w_idx] if w_idx < len(expected_weekly_inflows) else Decimal("0.0")
            ap_out = expected_weekly_ap_disbursements[w_idx] if w_idx < len(expected_weekly_ap_disbursements) else Decimal("0.0")
            payroll_out = expected_weekly_payroll[w_idx] if w_idx < len(expected_weekly_payroll) else Decimal("0.0")
            other_out = other_outflows[w_idx] if w_idx < len(other_outflows) else Decimal("0.0")

            total_outflows = ap_out + payroll_out + other_out
            net_change = inflows - total_outflows
            ending_cash = running_cash + net_change

            if ending_cash < min_projected_cash:
                min_projected_cash = ending_cash
                lowest_cash_week = w_idx + 1

            projection_schedule.append({
                "week_number": w_idx + 1,
                "week_start_date": week_start.isoformat(),
                "beginning_cash": float(running_cash),
                "total_inflows": float(inflows),
                "ap_disbursements": float(ap_out),
                "payroll_disbursements": float(payroll_out),
                "other_disbursements": float(other_out),
                "total_outflows": float(total_outflows),
                "net_cash_flow": float(net_change),
                "ending_cash": float(ending_cash)
            })

            running_cash = ending_cash

        return {
            "starting_cash_position": float(starting_cash_balance),
            "ending_cash_position": float(running_cash),
            "net_cumulative_cash_flow": float(running_cash - starting_cash_balance),
            "minimum_projected_cash": float(min_projected_cash),
            "lowest_cash_week": lowest_cash_week,
            "liquidity_risk": "DEFICIT_WARNING" if min_projected_cash < Decimal("0.0") else ("LOW_RESERVE" if min_projected_cash < Decimal("10000.0") else "ADEQUATE"),
            "weekly_schedule": projection_schedule
        }
