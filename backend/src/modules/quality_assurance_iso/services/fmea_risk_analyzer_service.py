"""
Failure Mode and Effects Analysis (FMEA) Risk Priority Number (RPN) Engine.
"""
from typing import Dict, Any

class FMEARiskAnalyzerService:
    @staticmethod
    def calculate_rpn(severity: int, occurrence: int, detection: int) -> Dict[str, Any]:
        rpn = severity * occurrence * detection
        
        tier = "LOW_RPN_ACCEPTABLE"
        if rpn >= 200 or severity >= 9:
            tier = "HIGH_RPN_CRITICAL"
        elif rpn >= 100:
            tier = "MEDIUM_RPN_MONITOR"

        return {
            "severity_rating": severity,
            "occurrence_rating": occurrence,
            "detection_rating": detection,
            "risk_priority_number_rpn": rpn,
            "risk_tier": tier,
            "corrective_action_mandatory": bool(tier == "HIGH_RPN_CRITICAL")
        }
