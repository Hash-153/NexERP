"""
NexERP Machine Downtime & Total Productive Maintenance (TPM) Pareto Analysis Engine.
Categorizes equipment stops by TPM failure modes:
- Mechanical Breakdown
- Electrical Failure
- Tooling Changeover / Setup
- Material Shortage / Starvation
- Sensor Jam / Minor Stoppages
- Operator Break / Idling
and computes cumulative duration percentages for 80/20 root cause prioritization.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List


class DowntimeParetoService:
    """
    Total Productive Maintenance (TPM) Downtime Pareto & MTBF/MTTR Analytics.
    """

    @classmethod
    def analyze_downtime_pareto(cls, downtime_events: List[Dict]) -> Dict:
        """
        Aggregate equipment downtime by reason code and generate Pareto distribution curve.
        """
        reason_durations = {}
        reason_event_counts = {}
        total_downtime_mins = Decimal("0.0")

        for event in downtime_events:
            reason = event.get("reason_category", "UNCATEGORIZED").upper()
            duration = Decimal(str(event.get("duration_minutes", 0)))
            reason_durations[reason] = reason_durations.get(reason, Decimal("0.0")) + duration
            reason_event_counts[reason] = reason_event_counts.get(reason, 0) + 1
            total_downtime_mins += duration

        # Sort descending by duration
        sorted_reasons = sorted(reason_durations.items(), key=lambda x: x[1], reverse=True)

        pareto_items = []
        cumulative_mins = Decimal("0.0")

        for rank, (reason, dur) in enumerate(sorted_reasons, start=1):
            cumulative_mins += dur
            pct_of_total = ((dur / total_downtime_mins) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_downtime_mins > Decimal("0.0") else Decimal("0.0")
            cum_pct = ((cumulative_mins / total_downtime_mins) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if total_downtime_mins > Decimal("0.0") else Decimal("0.0")

            pareto_items.append({
                "rank": rank,
                "reason_category": reason,
                "total_downtime_minutes": float(dur),
                "event_count": reason_event_counts[reason],
                "percentage_of_total": float(pct_of_total),
                "cumulative_percentage": float(cum_pct),
                "is_vital_few_80_percent": cum_pct <= Decimal("80.0") or (rank == 1)
            })

        return {
            "total_downtime_minutes": float(total_downtime_mins),
            "total_stoppage_events": len(downtime_events),
            "top_failure_cause": sorted_reasons[0][0] if sorted_reasons else None,
            "pareto_distribution": pareto_items
        }

    @classmethod
    def calculate_reliability_metrics(
        cls,
        total_operating_hours: Decimal,
        failure_count: int,
        total_repair_time_hours: Decimal
    ) -> Dict:
        """
        Calculate Mean Time Between Failures (MTBF), Mean Time To Repair (MTTR), and Inherent Availability (Ai).
        """
        if failure_count <= 0:
            mtbf = total_operating_hours
            mttr = Decimal("0.0")
            availability = Decimal("100.0")
        else:
            mtbf = (total_operating_hours / Decimal(str(failure_count))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            mttr = (total_repair_time_hours / Decimal(str(failure_count))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            availability = ((mtbf / (mtbf + mttr)) * Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if (mtbf + mttr) > Decimal("0.0") else Decimal("0.0")

        return {
            "total_operating_hours": float(total_operating_hours),
            "failure_count": failure_count,
            "mean_time_between_failures_mtbf_hours": float(mtbf),
            "mean_time_to_repair_mttr_hours": float(mttr),
            "inherent_availability_percent": float(availability)
        }
