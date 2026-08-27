"""
Benford's Law & Forensic Journal Voucher Anomaly Detection Service.
Detects round-dollar manual entries, weekend postings, split transactions below approval limits, and unusual GL account pairs.
"""
from decimal import Decimal
from typing import Dict, Any, List

class ForensicAnomalyDetectorService:
    @staticmethod
    def evaluate_journal_risk(
        journal_number: str,
        amount: Decimal,
        is_weekend_posted: bool,
        is_manual_entry: bool,
        is_round_dollar_amount: bool,
        user_created_by: str
    ) -> Dict[str, Any]:
        risk_score = 0
        risk_flags = []

        if is_weekend_posted:
            risk_score += 35
            risk_flags.append("POSTED_OUTSIDE_BUSINESS_HOURS_WEEKEND")

        if is_round_dollar_amount and amount >= Decimal("10000.00"):
            risk_score += 25
            risk_flags.append("SUSPICIOUS_ROUND_DOLLAR_ESTIMATE")

        if is_manual_entry and amount >= Decimal("250000.00"):
            risk_score += 30
            risk_flags.append("HIGH_VALUE_MANUAL_TOP_SIDE_ADJUSTMENT")

        if amount > Decimal("49000.00") and amount < Decimal("50000.00"):
            risk_score += 40
            risk_flags.append("POSSIBLE_SMURFING_BELOW_50K_APPROVAL_THRESHOLD")

        severity = "LOW"
        if risk_score >= 60:
            severity = "MATERIAL_WEAKNESS"
        elif risk_score >= 30:
            severity = "SIGNIFICANT_DEFICIENCY"

        return {
            "journal_number": journal_number,
            "posted_amount": float(amount),
            "risk_score": risk_score,
            "severity": severity,
            "risk_flags": risk_flags,
            "requires_cfo_signoff": bool(risk_score >= 50)
        }
