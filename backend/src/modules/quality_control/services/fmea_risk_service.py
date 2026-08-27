"""
NexERP Failure Mode and Effects Analysis (FMEA) Risk Prioritization Engine.
Calculates Risk Priority Number (RPN = Severity x Occurrence x Detection)
and AIAG/VDA Action Priority (High, Medium, Low).
"""

from typing import Dict, List


class FMEARiskService:
    """
    Process & Design Failure Mode and Effects Analysis (FMEA) Service.
    """

    @classmethod
    def calculate_rpn(
        cls,
        severity: int,
        occurrence: int,
        detection: int
    ) -> Dict:
        """
        Compute RPN score and determine AIAG/VDA Action Priority tier.
        """
        for val, name in [(severity, "Severity"), (occurrence, "Occurrence"), (detection, "Detection")]:
            if val < 1 or val > 10:
                raise ValueError(f"{name} rating ({val}) must be an integer between 1 and 10.")

        rpn = severity * occurrence * detection

        # AIAG/VDA Action Priority Logic
        if severity >= 9 or (severity >= 7 and occurrence >= 4) or rpn >= 200:
            action_priority = "HIGH"
            recommendation = "Immediate engineering countermeasure required before mass production release."
        elif severity >= 5 and occurrence >= 4 or rpn >= 100:
            action_priority = "MEDIUM"
            recommendation = "Improve error-proofing (Poka-Yoke) or detection controls."
        else:
            action_priority = "LOW"
            recommendation = "Current controls and standard operating procedures are acceptable."

        return {
            "severity": severity,
            "occurrence": occurrence,
            "detection": detection,
            "risk_priority_number_rpn": rpn,
            "action_priority": action_priority,
            "engineering_recommendation": recommendation
        }

    @classmethod
    def rank_fmea_failure_modes(cls, failure_modes: List[Dict]) -> List[Dict]:
        """
        Evaluate and sort multiple potential failure modes in descending order of critical risk.
        """
        evaluated = []
        for fm in failure_modes:
            res = cls.calculate_rpn(
                severity=fm["severity"],
                occurrence=fm["occurrence"],
                detection=fm["detection"]
            )
            item = dict(fm)
            item.update(res)
            evaluated.append(item)

        # Sort primarily by Action Priority (HIGH > MEDIUM > LOW), then by RPN descending
        priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
        evaluated.sort(key=lambda x: (priority_order.get(x["action_priority"], 3), -x["risk_priority_number_rpn"]))
        return evaluated
