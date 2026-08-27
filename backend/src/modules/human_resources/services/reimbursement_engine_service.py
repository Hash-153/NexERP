"""
NexERP Travel & Expense (T&E) Reimbursement Engine.
Calculates IRS standard mileage reimbursements, GSA federal per diem rates for lodging and meals,
foreign currency travel receipts, and automated AP disbursement creation.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class ReimbursementEngineService:
    """
    Travel & Employee Expense Reimbursement Calculation Service.
    """

    @classmethod
    def calculate_mileage_reimbursement(
        cls,
        miles_driven: Decimal,
        irs_rate_per_mile: Decimal = Decimal("0.67")
    ) -> Dict:
        """
        Compute standard tax-deductible vehicle business mileage reimbursement.
        """
        reimbursement = (miles_driven * irs_rate_per_mile).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return {
            "miles_driven": float(miles_driven),
            "rate_per_mile": float(irs_rate_per_mile),
            "total_reimbursement_amount": float(reimbursement)
        }

    @classmethod
    def audit_expense_claim_compliance(
        cls,
        expense_items: List[Dict],
        daily_meal_per_diem_limit: Decimal = Decimal("79.00"),
        receipt_required_threshold: Decimal = Decimal("25.00")
    ) -> Dict:
        """
        Audit submitted employee expense report against corporate travel policy rules.
        """
        violations = []
        total_approved = Decimal("0.0")
        total_flagged = Decimal("0.0")

        for item in expense_items:
            amt = Decimal(str(item.get("amount", 0.0)))
            cat = str(item.get("category", "GENERAL")).upper()
            has_receipt = bool(item.get("has_receipt", False))

            if amt > receipt_required_threshold and not has_receipt:
                violations.append({
                    "item_description": item.get("description", "Expense Item"),
                    "amount": float(amt),
                    "violation_code": "MISSING_RECEIPT",
                    "message": f"Receipt mandatory for expenses exceeding ${receipt_required_threshold}."
                })
                total_flagged += amt
            elif cat == "MEALS" and amt > daily_meal_per_diem_limit:
                violations.append({
                    "item_description": item.get("description", "Meal"),
                    "amount": float(amt),
                    "violation_code": "EXCEEDS_PER_DIEM",
                    "message": f"Meal expense exceeds daily per diem cap of ${daily_meal_per_diem_limit}."
                })
                total_flagged += amt
            else:
                total_approved += amt

        return {
            "total_claim_amount": float(total_approved + total_flagged),
            "total_approved_amount": float(total_approved),
            "total_flagged_amount": float(total_flagged),
            "is_fully_compliant": len(violations) == 0,
            "policy_violations": violations
        }
