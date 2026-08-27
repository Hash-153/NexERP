"""
Multi-Dimensional OLAP Cube Aggregation Service for Ad-Hoc Business Intelligence.
"""
from decimal import Decimal
from typing import Dict, Any, List

class DataCubeAnalyticsService:
    @staticmethod
    def aggregate_by_dimensions(
        facts: List[Dict[str, Any]],
        dimension_keys: List[str],
        metric_key: str
    ) -> List[Dict[str, Any]]:
        groups: Dict[tuple, Decimal] = {}
        counts: Dict[tuple, int] = {}

        for fact in facts:
            dim_values = tuple(fact.get(k, "UNKNOWN") for k in dimension_keys)
            val = Decimal(str(fact.get(metric_key, 0)))
            groups[dim_values] = groups.get(dim_values, Decimal("0.0")) + val
            counts[dim_values] = counts.get(dim_values, 0) + 1

        results = []
        for dim_tuple, total_metric in groups.items():
            record = {k: v for k, v in zip(dimension_keys, dim_tuple)}
            record[f"total_{metric_key}"] = float(total_metric)
            record["record_count"] = counts[dim_tuple]
            results.append(record)

        return sorted(results, key=lambda x: x.get(f"total_{metric_key}", 0), reverse=True)
