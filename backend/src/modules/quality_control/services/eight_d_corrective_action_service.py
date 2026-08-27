"""
NexERP 8D Problem Solving & Corrective/Preventive Action (CAPA) Engine.
Implements the Automotive Industry standard 8D (Eight Disciplines) methodology:
- D1: Establish the Cross-Functional Team
- D2: Describe the Problem (5W2H)
- D3: Implement Immediate Containment Action (ICA)
- D4: Determine Root Causes (5-Why & Ishikawa Fishbone)
- D5: Choose Permanent Corrective Actions (PCA)
- D6: Implement and Validate PCA
- D7: Prevent Recurrence (Standardization & FMEA update)
- D8: Congratulate the Team & Formal Closeout
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional


class EightDCorrectiveActionService:
    """
    Automotive 8D Problem Solving and CAPA Quality Service.
    """

    EIGHT_D_DISCIPLINES = [
        ("D1_TEAM", "Establish the Team"),
        ("D2_PROBLEM", "Define Problem Statement (5W2H)"),
        ("D3_CONTAINMENT", "Develop Interim Containment Actions (ICA)"),
        ("D4_ROOT_CAUSE", "Identify Root Cause (5-Whys / Fishbone)"),
        ("D5_CHOOSE_PCA", "Formulate Permanent Corrective Actions (PCA)"),
        ("D6_VALIDATE_PCA", "Implement & Validate Permanent Corrective Actions"),
        ("D7_PREVENT_RECURRENCE", "Prevent Recurrence / Update Control Plans & SOPs"),
        ("D8_CONGRATULATE_TEAM", "Recognize Team Contributions & Close 8D Report")
    ]

    @classmethod
    def structure_8d_investigation(
        cls,
        report_number: str,
        issue_title: str,
        item_sku: str,
        customer_or_vendor: str,
        team_leader: str,
        team_members: List[str],
        problem_description_5w2h: Dict[str, str],
        containment_action: str,
        five_whys: List[str],
        root_cause_summary: str,
        corrective_actions: List[Dict[str, str]]
    ) -> Dict:
        """
        Synthesize a full 8D non-conformance investigation document.
        """
        if len(five_whys) < 3:
            raise ValueError("Root cause analysis must include at least 3 levels of 5-Why progression.")

        return {
            "report_number": report_number,
            "issue_title": issue_title,
            "item_sku": item_sku,
            "external_party": customer_or_vendor,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "D6_VALIDATION_IN_PROGRESS",
            "disciplines": {
                "D1_team": {
                    "leader": team_leader,
                    "members": team_members
                },
                "D2_problem_statement": problem_description_5w2h,
                "D3_interim_containment": {
                    "action": containment_action,
                    "quarantine_applied": True,
                    "customer_risk_contained": True
                },
                "D4_root_cause_analysis": {
                    "five_whys_drilldown": five_whys,
                    "verified_root_cause": root_cause_summary
                },
                "D5_permanent_corrective_actions": corrective_actions,
                "D6_implementation_verification": {
                    "validation_method": "100% Inspection on next 3 production batches",
                    "target_completion_date": "Within 30 calendar days"
                },
                "D7_systemic_prevention": {
                    "fmea_updated": True,
                    "control_plan_revised": True,
                    "operator_training_completed": True
                },
                "D8_closeout": {
                    "signoff_quality_manager": None,
                    "is_closed": False
                }
            }
        }
