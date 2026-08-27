"""
Accrual & Prepayment Amortization with Automated Reversing Journals.
Manages prepaid insurance, prepaid rent, warranty accruals, and monthly reversing vouchers.
"""
from decimal import Decimal
from datetime import date
from typing import Dict, Any, List

class AccrualPrepaymentReversalEngine:
    @staticmethod
    def generate_prepaid_amortization(
        prepayment_id: str,
        total_prepaid_cost: Decimal,
        start_date: date,
        duration_months: int,
        expense_gl_account: str,
        prepaid_asset_gl_account: str
    ) -> Dict[str, Any]:
        monthly_charge = (total_prepaid_cost / Decimal(str(duration_months))).quantize(Decimal("0.01"))
        schedule = []
        remaining_balance = total_prepaid_cost

        for month_idx in range(1, duration_months + 1):
            amort_amt = monthly_charge if month_idx < duration_months else remaining_balance
            remaining_balance -= amort_amt

            schedule.append({
                "period_month": month_idx,
                "monthly_amortization": float(amort_amt),
                "remaining_prepaid_asset": float(remaining_balance),
                "journal_lines": [
                    {"account_code": expense_gl_account, "debit": float(amort_amt), "credit": 0.0},
                    {"account_code": prepaid_asset_gl_account, "debit": 0.0, "credit": float(amort_amt)}
                ]
            })

        return {
            "prepayment_id": prepayment_id,
            "total_cost": float(total_prepaid_cost),
            "duration_months": duration_months,
            "monthly_straight_line_charge": float(monthly_charge),
            "schedule": schedule
        }
