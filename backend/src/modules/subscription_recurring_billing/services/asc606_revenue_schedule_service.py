"""
ASC 606 / IFRS 15 SaaS Deferred Revenue Recognition Waterfall Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List

class ASC606RevenueScheduleService:
    @staticmethod
    def generate_recognition_waterfall(
        total_contract_value: Decimal,
        term_months: int = 12
    ) -> Dict[str, Any]:
        monthly_rec = (total_contract_value / Decimal(str(term_months))).quantize(Decimal("0.01"))
        schedule = []
        deferred = total_contract_value

        for m in range(1, term_months + 1):
            rec_amt = monthly_rec if m < term_months else deferred
            deferred -= rec_amt

            schedule.append({
                "month_index": m,
                "recognized_revenue": float(rec_amt),
                "ending_deferred_revenue_balance": float(deferred),
                "amortization_percentage": round((m / term_months) * 100, 2)
            })

        return {
            "total_contract_value": float(total_contract_value),
            "term_months": term_months,
            "monthly_run_rate": float(monthly_rec),
            "waterfall_schedule": schedule
        }
