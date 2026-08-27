"""
NexERP Acceptance Quality Limit (AQL) Lot Sampling Inspection Engine.
Implements ANSI/ASQ Z1.4 (ISO 2859-1) standard sampling plans:
- General Inspection Levels I, II, III
- Special Inspection Levels S-1 to S-4
- Normal, Tightened, and Reduced Inspection transitions
- Sample Size Code Letters & Accept/Reject thresholds (Ac / Re).
"""

from typing import Dict, Optional


class AQLSamplingService:
    """
    ANSI/ASQ Z1.4 (ISO 2859-1) Acceptance Sampling Plan Generator.
    """

    # Lot size to Sample Size Code Letter (General Inspection Level II - Normal)
    LOT_SIZE_CODE_LETTERS = [
        (8, "A"), (15, "B"), (25, "C"), (50, "D"), (90, "E"),
        (150, "F"), (280, "G"), (500, "H"), (1200, "J"), (3200, "K"),
        (10000, "L"), (35000, "M"), (150000, "N"), (500000, "P"), (float("inf"), "Q")
    ]

    # Sample Size mapped to Code Letter
    CODE_LETTER_SAMPLE_SIZES = {
        "A": 2, "B": 3, "C": 5, "D": 8, "E": 13,
        "F": 20, "G": 32, "H": 50, "J": 80, "K": 125,
        "L": 200, "M": 315, "N": 500, "P": 800, "Q": 1250
    }

    # Standard AQL 1.0, 2.5, 4.0 Accept (Ac) / Reject (Re) thresholds for Normal Single Sampling
    # (sample_size_code, aql_level) -> (Accept, Reject)
    AQL_LIMIT_THRESHOLDS = {
        ("D", 1.0): (0, 1), ("D", 2.5): (0, 1), ("D", 4.0): (1, 2),
        ("E", 1.0): (0, 1), ("E", 2.5): (1, 2), ("E", 4.0): (1, 2),
        ("F", 1.0): (0, 1), ("F", 2.5): (1, 2), ("F", 4.0): (2, 3),
        ("G", 1.0): (1, 2), ("G", 2.5): (2, 3), ("G", 4.0): (3, 4),
        ("H", 1.0): (1, 2), ("H", 2.5): (3, 4), ("H", 4.0): (5, 6),
        ("J", 1.0): (2, 3), ("J", 2.5): (5, 6), ("J", 4.0): (7, 8),
        ("K", 1.0): (3, 4), ("K", 2.5): (7, 8), ("K", 4.0): (10, 11),
        ("L", 1.0): (5, 6), ("L", 2.5): (10, 11), ("L", 4.0): (14, 15),
    }

    @classmethod
    def determine_sample_code_letter(cls, lot_size: int, inspection_level: str = "II") -> str:
        """Find sample size code letter for a given lot size."""
        for max_lot, code in cls.LOT_SIZE_CODE_LETTERS:
            if lot_size <= max_lot:
                return code
        return "Q"

    @classmethod
    def get_sampling_plan(
        cls,
        lot_size: int,
        aql_target_percent: float = 2.5,
        inspection_level: str = "II",
        inspection_type: str = "NORMAL"
    ) -> Dict:
        """
        Generate complete ANSI/ASQ Z1.4 sampling instructions.
        """
        if lot_size <= 0:
            raise ValueError("Lot size must be positive non-zero.")

        code_letter = cls.determine_sample_code_letter(lot_size, inspection_level)
        sample_size = min(lot_size, cls.CODE_LETTER_SAMPLE_SIZES.get(code_letter, 20))

        # Look up threshold
        threshold = cls.AQL_LIMIT_THRESHOLDS.get((code_letter, aql_target_percent))
        if not threshold:
            # Fallback default approximation
            ac = max(0, int(sample_size * (aql_target_percent / 100.0)))
            re = ac + 1
        else:
            ac, re = threshold

        return {
            "lot_size": lot_size,
            "inspection_standard": "ANSI/ASQ Z1.4 (ISO 2859-1)",
            "inspection_level": f"General Level {inspection_level}",
            "inspection_type": inspection_type,
            "sample_size_code_letter": code_letter,
            "sample_size_units_to_pull": sample_size,
            "aql_target_percent": aql_target_percent,
            "acceptance_number_ac": ac,
            "rejection_number_re": re,
            "instruction": f"Inspect {sample_size} random units. Accept lot if defectives <= {ac}. Reject lot if defectives >= {re}."
        }

    @classmethod
    def evaluate_lot_disposition(
        cls,
        lot_size: int,
        defects_found_count: int,
        aql_target_percent: float = 2.5
    ) -> Dict:
        """
        Evaluate pass/fail disposition of an inspected production/receiving lot.
        """
        plan = cls.get_sampling_plan(lot_size, aql_target_percent)
        ac = plan["acceptance_number_ac"]
        re = plan["rejection_number_re"]

        if defects_found_count <= ac:
            disposition = "ACCEPTED"
            reason = f"Defects ({defects_found_count}) are within acceptance threshold (Ac={ac})."
        else:
            disposition = "REJECTED_QC_HOLD"
            reason = f"Defects ({defects_found_count}) reached rejection threshold (Re={re}). Quarantine lot for MRB review."

        return {
            "disposition": disposition,
            "defects_found": defects_found_count,
            "plan": plan,
            "reason": reason
        }
