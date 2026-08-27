"""
NexERP Multi-Tier Automated Dunning & Collection Escalation Engine.
Manages dunning levels:
- Level 1: Friendly Reminder (1-14 days past due) - 0% interest
- Level 2: Formal Notice (15-30 days past due) - 1.5% statutory late interest
- Level 3: Demand for Payment (31-60 days past due) - Account placed on Credit Hold
- Level 4: Final Legal Notice / Collection Agency referral (60+ days past due).
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class DunningEscalationService:
    """
    Accounts Receivable Automated Dunning and Interest Calculation Service.
    """

    DUNNING_LEVELS = {
        1: {"title": "Friendly Reminder", "min_days_past_due": 1, "interest_rate_percent": Decimal("0.0"), "action": "EMAIL_REMINDER"},
        2: {"title": "Formal Payment Notice", "min_days_past_due": 15, "interest_rate_percent": Decimal("1.5"), "action": "FORMAL_LETTER"},
        3: {"title": "Urgent Demand & Credit Hold", "min_days_past_due": 31, "interest_rate_percent": Decimal("2.0"), "action": "CREDIT_HOLD_ENFORCED"},
        4: {"title": "Final Notice of Legal Action", "min_days_past_due": 61, "interest_rate_percent": Decimal("2.5"), "action": "LEGAL_COLLECTIONS_REFERRAL"},
    }

    @classmethod
    def evaluate_dunning_level(
        cls,
        invoice_number: str,
        customer_name: str,
        principal_amount: Decimal,
        due_date: date,
        as_of_date: date
    ) -> Dict:
        """
        Evaluate applicable dunning tier, compute statutory late fee interest, and draft message.
        """
        days_overdue = (as_of_date - due_date).days
        if days_overdue <= 0:
            return {
                "invoice_number": invoice_number,
                "status": "NOT_OVERDUE",
                "days_overdue": 0,
                "dunning_level": 0,
                "interest_charged": 0.0,
                "total_payable": float(principal_amount)
            }

        # Determine level
        selected_level = 1
        for lvl in [4, 3, 2, 1]:
            if days_overdue >= cls.DUNNING_LEVELS[lvl]["min_days_past_due"]:
                selected_level = lvl
                break

        level_info = cls.DUNNING_LEVELS[selected_level]
        interest_rate = level_info["interest_rate_percent"]
        # Calculate monthly compounding interest
        interest_amount = (principal_amount * (interest_rate / Decimal("100.0")) * (Decimal(str(days_overdue)) / Decimal("30.0"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total_payable = principal_amount + interest_amount

        return {
            "invoice_number": invoice_number,
            "customer_name": customer_name,
            "principal_amount": float(principal_amount),
            "due_date": due_date.isoformat(),
            "as_of_date": as_of_date.isoformat(),
            "days_overdue": days_overdue,
            "dunning_level": selected_level,
            "dunning_level_title": level_info["title"],
            "statutory_action": level_info["action"],
            "late_interest_rate_monthly_percent": float(interest_rate),
            "accrued_interest_penalty": float(interest_amount),
            "total_balance_payable": float(total_payable)
        }
