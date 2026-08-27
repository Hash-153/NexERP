"""
NexERP Succession Planning & 9-Box Talent Matrix Engine.
Maps:
- Performance Rating (1=Low, 2=Medium, 3=High) vs Potential Rating (1=Low, 2=Medium, 3=High)
- 9-Box Box Categories (Star, High Potential, Core Player, Risk, etc.)
- Bench Strength & Succession Readiness Timeframes (Ready Now, 1-2 Years, 3+ Years).
"""

from typing import Dict, List, Optional


class SuccessionPlanningService:
    """
    9-Box Grid Talent Management & Succession Pipeline Service.
    """

    NINE_BOX_MATRIX = {
        (3, 3): {"box_name": "STAR", "action": "High-priority successor; accelerate leadership development."},
        (3, 2): {"box_name": "HIGH_PERFORMER", "action": "Broaden role scope and strategic assignments."},
        (3, 1): {"box_name": "SOLID_PROFESSIONAL", "action": "Key contributor in current role; maximize expertise."},
        (2, 3): {"box_name": "HIGH_POTENTIAL", "action": "Provide stretch assignments and executive mentoring."},
        (2, 2): {"box_name": "CORE_PLAYER", "action": "Steady performer; support ongoing skill enhancement."},
        (2, 1): {"box_name": "EFFECTIVE_PERFORMER", "action": "Monitor progress and coach on development areas."},
        (1, 3): {"box_name": "ENIGMA", "action": "Identify performance blockers; re-align role expectations."},
        (1, 2): {"box_name": "DILEMMA", "action": "Structured performance improvement plan (PIP)."},
        (1, 1): {"box_name": "RISK", "action": "Evaluate re-assignment or exit transition."},
    }

    @classmethod
    def evaluate_employee_talent_position(
        cls,
        employee_id: str,
        employee_name: str,
        current_job_title: str,
        performance_score_1_to_3: int,
        potential_score_1_to_3: int,
        readiness_for_promotion: str = "READY_IN_1_TO_2_YEARS"
    ) -> Dict:
        """
        Evaluate employee 9-box placement and succession pipeline recommendation.
        """
        perf = max(1, min(3, performance_score_1_to_3))
        pot = max(1, min(3, potential_score_1_to_3))

        box_info = cls.NINE_BOX_MATRIX.get((perf, pot), {"box_name": "CORE_PLAYER", "action": "Maintain development."})

        return {
            "employee_id": employee_id,
            "employee_name": employee_name,
            "current_title": current_job_title,
            "performance_level": perf,
            "potential_level": pot,
            "nine_box_classification": box_info["box_name"],
            "talent_development_action": box_info["action"],
            "readiness_timeframe": readiness_for_promotion.upper(),
            "is_high_flight_risk_asset": box_info["box_name"] in ["STAR", "HIGH_POTENTIAL"]
        }
