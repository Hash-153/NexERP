"""
NexERP Employee Performance Management, Goal Cascading & Talent Review Engine.
Supports annual/quarterly 360 appraisal cycles, OKR achievement scoring,
competency ratings, and 9-Box talent grid categorization.
"""

from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class PerformanceReviewService:
    """
    Talent Management & Performance Appraisal Service.
    """

    @classmethod
    def calculate_appraisal_score(
        cls,
        goal_scores: List[Dict],
        competency_scores: List[Dict],
        goals_weight: Decimal = Decimal("0.60"),
        competencies_weight: Decimal = Decimal("0.40")
    ) -> Dict:
        """
        Calculate composite appraisal score (1.0 to 5.0 scale) combining Key Results/OKRs and Core Competencies.
        """
        if not goal_scores or not competency_scores:
            return {
                "composite_score": 3.0,
                "rating_label": "MEETS_EXPECTATIONS",
                "merit_increase_recommended_percent": 3.0
            }

        # Weighted Goal Score
        total_goal_weighted = sum(
            Decimal(str(g["score"])) * (Decimal(str(g.get("weight", 1.0))) / Decimal(str(sum(x.get("weight", 1.0) for x in goal_scores))))
            for g in goal_scores
        )

        # Average Competency Score
        avg_competency = sum(Decimal(str(c["score"])) for c in competency_scores) / Decimal(str(len(competency_scores)))

        composite = ((total_goal_weighted * goals_weight) + (avg_competency * competencies_weight)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if composite >= Decimal("4.5"):
            label = "EXCEEDS_EXPECTATIONS_DISTINGUISHED"
            merit_pct = Decimal("6.5")
            nine_box = "TOP_TALENT_STAR"
        elif composite >= Decimal("3.5"):
            label = "MEETS_EXPECTATIONS_STRONG"
            merit_pct = Decimal("4.0")
            nine_box = "HIGH_PERFORMER_CORE"
        elif composite >= Decimal("2.5"):
            label = "DEVELOPMENT_NEEDED"
            merit_pct = Decimal("1.5")
            nine_box = "EFFECTIVE_SOLID"
        else:
            label = "UNSATISFACTORY_PIP"
            merit_pct = Decimal("0.0")
            nine_box = "UNDERPERFORMER_RISK"

        return {
            "goals_weighted_score": float(total_goal_weighted.quantize(Decimal("0.01"))),
            "competencies_average_score": float(avg_competency.quantize(Decimal("0.01"))),
            "composite_score": float(composite),
            "performance_rating_label": label,
            "nine_box_talent_quadrant": nine_box,
            "merit_increase_recommended_percent": float(merit_pct)
        }
