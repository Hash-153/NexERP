"""
NexERP Statistical Process Control (SPC) & Six Sigma Capability Engine.
Computes Shewhart X-bar and R control charts, control limits (UCL, LCL),
and process capability indices (Cp, Cpk, Pp, Ppk).
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class SPCControlChartService:
    """
    Six Sigma Statistical Process Control & Capability Service.
    """

    # ASTM E2587 / ISO 7870-2 Constants for X-bar and R charts (subgroup size n = 2 to 10)
    A2_CONSTANTS = {
        2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577,
        6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308
    }
    D3_CONSTANTS = {
        2: 0.0, 3: 0.0, 4: 0.0, 5: 0.0,
        6: 0.0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223
    }
    D4_CONSTANTS = {
        2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114,
        6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777
    }
    D2_CONSTANTS = {
        2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326,
        6: 2.534, 7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078
    }

    @classmethod
    def calculate_xbar_r_control_chart(
        cls,
        subgroups: List[List[float]],
        upper_spec_limit: Optional[float] = None,
        lower_spec_limit: Optional[float] = None
    ) -> Dict:
        """
        Compute subgroup averages, ranges, grand mean, average range, UCL/LCL, and Cp/Cpk.
        """
        if not subgroups or len(subgroups) < 2:
            raise ValueError("At least 2 subgroups are required for SPC analysis.")

        subgroup_size = len(subgroups[0])
        if subgroup_size < 2 or subgroup_size > 10:
            raise ValueError(f"Subgroup size ({subgroup_size}) must be between 2 and 10.")

        subgroup_means = [sum(sg) / len(sg) for sg in subgroups]
        subgroup_ranges = [max(sg) - min(sg) for sg in subgroups]

        x_double_bar = sum(subgroup_means) / len(subgroup_means)
        r_bar = sum(subgroup_ranges) / len(subgroup_ranges)

        a2 = cls.A2_CONSTANTS.get(subgroup_size, 0.577)
        d3 = cls.D3_CONSTANTS.get(subgroup_size, 0.0)
        d4 = cls.D4_CONSTANTS.get(subgroup_size, 2.114)
        d2 = cls.D2_CONSTANTS.get(subgroup_size, 2.326)

        # Control Limits for X-bar
        ucl_x = x_double_bar + (a2 * r_bar)
        lcl_x = x_double_bar - (a2 * r_bar)

        # Control Limits for Range
        ucl_r = d4 * r_bar
        lcl_r = d3 * r_bar

        # Estimated Process Standard Deviation (sigma = R_bar / d2)
        sigma_within = r_bar / d2 if d2 > 0 else 0.0001

        # Process Capability Indices
        cp = None
        cpk = None
        if upper_spec_limit is not None and lower_spec_limit is not None and sigma_within > 0:
            cp = round((upper_spec_limit - lower_spec_limit) / (6 * sigma_within), 4)
            cpu = (upper_spec_limit - x_double_bar) / (3 * sigma_within)
            cpl = (x_double_bar - lower_spec_limit) / (3 * sigma_within)
            cpk = round(min(cpu, cpl), 4)

        # Check for Out-of-Control Points (Western Electric Rule 1: 1 point beyond 3-sigma)
        out_of_control_x = [i + 1 for i, m in enumerate(subgroup_means) if m > ucl_x or m < lcl_x]
        out_of_control_r = [i + 1 for i, r in enumerate(subgroup_ranges) if r > ucl_r or r < lcl_r]

        process_state = "STATISTICAL_CONTROL" if (not out_of_control_x and not out_of_control_r) else "OUT_OF_CONTROL"

        return {
            "subgroups_count": len(subgroups),
            "subgroup_size": subgroup_size,
            "grand_mean_x_double_bar": round(x_double_bar, 4),
            "average_range_r_bar": round(r_bar, 4),
            "estimated_sigma_within": round(sigma_within, 4),
            "xbar_limits": {
                "ucl": round(ucl_x, 4),
                "center_line": round(x_double_bar, 4),
                "lcl": round(lcl_x, 4)
            },
            "range_limits": {
                "ucl": round(ucl_r, 4),
                "center_line": round(r_bar, 4),
                "lcl": round(lcl_r, 4)
            },
            "process_capability": {
                "cp": cp,
                "cpk": cpk,
                "capability_rating": "EXCELLENT_SIX_SIGMA" if (cpk and cpk >= 1.67) else ("CAPABLE" if (cpk and cpk >= 1.33) else ("MARGINAL" if (cpk and cpk >= 1.0) else "INCAPABLE"))
            },
            "process_state": process_state,
            "violations": {
                "out_of_control_x_points": out_of_control_x,
                "out_of_control_r_points": out_of_control_r
            }
        }
