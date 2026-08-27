"""
Supplier Performance Scorecard & On-Time In-Full (OTIF) Quality Engine.
"""
from decimal import Decimal
from typing import Dict, Any, List

class VendorScorecardEngineService:
    @staticmethod
    def calculate_vendor_grade(
        total_po_lines: int,
        on_time_lines: int,
        in_full_lines: int,
        defective_parts: int,
        total_parts_delivered: int,
        price_variance_pct: Decimal = Decimal("0.0")
    ) -> Dict[str, Any]:
        otif_lines = min(on_time_lines, in_full_lines)
        otif_pct = ((Decimal(str(otif_lines)) / Decimal(str(total_po_lines))) * Decimal("100.0")).quantize(Decimal("0.01")) if total_po_lines > 0 else Decimal("0.0")
        
        ppm_defects = (Decimal(str(defective_parts)) / Decimal(str(total_parts_delivered)) * Decimal("1000000.0")).quantize(Decimal("0.01")) if total_parts_delivered > 0 else Decimal("0.0")
        
        # Weighted Composite Score (40% OTIF, 40% PPM Quality, 20% Price Variance)
        quality_score = max(Decimal("0.0"), Decimal("100.0") - (ppm_defects / Decimal("50.0")))
        delivery_score = otif_pct
        price_score = max(Decimal("0.0"), Decimal("100.0") - (abs(price_variance_pct) * Decimal("5.0")))

        composite = (delivery_score * Decimal("0.40") + quality_score * Decimal("0.40") + price_score * Decimal("0.20")).quantize(Decimal("0.01"))
        
        if composite >= Decimal("90.0"):
            grade = "TIER_1_PREFERRED"
        elif composite >= Decimal("75.0"):
            grade = "TIER_2_QUALIFIED"
        elif composite >= Decimal("60.0"):
            grade = "TIER_3_CONDITIONAL_CAP_REQUIRED"
        else:
            grade = "TIER_4_DISQUALIFIED_OFFBOARD"

        return {
            "composite_score": float(composite),
            "performance_grade": grade,
            "otif_delivery_percentage": float(otif_pct),
            "ppm_defect_rate": float(ppm_defects),
            "quality_subscore": float(quality_score),
            "delivery_subscore": float(delivery_score),
            "price_variance_subscore": float(price_score)
        }
