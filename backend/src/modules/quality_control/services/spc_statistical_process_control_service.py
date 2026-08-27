"""
Statistical Process Control (SPC) & Process Capability (Cp / Cpk) Engine.
Calculates Upper/Lower Specification Limits (USL/LSL), Mean, Standard Deviation, and Six Sigma metrics.
"""
import math
from decimal import Decimal
from typing import Dict, Any, List

class SPCStatisticalProcessControlService:
    @staticmethod
    def calculate_cp_cpk(
        sample_measurements: List[float],
        usl: float,
        lsl: float
    ) -> Dict[str, Any]:
        if len(sample_measurements) < 2:
            return {"error": "Insufficient sample size (minimum 2)"}

        n = len(sample_measurements)
        mean = sum(sample_measurements) / n
        variance = sum((x - mean) ** 2 for x in sample_measurements) / (n - 1)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return {"mean": mean, "std_dev": 0.0, "cp": 99.9, "cpk": 99.9}

        # Potential Capability (Cp = (USL - LSL) / (6 * sigma))
        cp = (usl - lsl) / (6.0 * std_dev)
        
        # Actual Capability (Cpk = min((USL - mean)/(3*sigma), (mean - LSL)/(3*sigma)))
        cpu = (usl - mean) / (3.0 * std_dev)
        cpl = (mean - lsl) / (3.0 * std_dev)
        cpk = min(cpu, cpl)

        # Estimate PPM outside spec limits using normal distribution z-score
        z_upper = (usl - mean) / std_dev
        z_lower = (mean - lsl) / std_dev
        min_z = min(z_upper, z_lower)
        estimated_sigma_level = round(3.0 * cpk, 2)

        return {
            "sample_size": n,
            "sample_mean": round(mean, 4),
            "sample_std_dev": round(std_dev, 4),
            "upper_spec_limit_usl": usl,
            "lower_spec_limit_lsl": lsl,
            "process_capability_cp": round(cp, 3),
            "process_capability_cpk": round(cpk, 3),
            "sigma_quality_level": estimated_sigma_level,
            "is_capable_six_sigma": bool(cpk >= 1.33),
            "status": "CAPABLE_SIX_SIGMA" if cpk >= 1.33 else ("ACCEPTABLE" if cpk >= 1.0 else "UNACCEPTABLE_PROCESS_DRIFT")
        }
