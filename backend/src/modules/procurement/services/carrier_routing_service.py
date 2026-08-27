"""
NexERP Transportation Management (TMS) Carrier Rating & Freight Lane Optimization Engine.
Calculates Less-Than-Truckload (LTL) and Full-Truckload (FTL) freight costs,
mileage rate tables, accessorial charges (liftgate, residential, detention),
and dynamic weekly Fuel Surcharge Index (FSI) adjustments.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class CarrierRatingService:
    """
    TMS Freight Rating and Carrier Selection Service.
    """

    # National Diesel Fuel Price baseline index ($/gal -> Fuel Surcharge %)
    FUEL_SURCHARGE_TABLE = [
        (Decimal("3.00"), Decimal("0.12")),
        (Decimal("3.50"), Decimal("0.16")),
        (Decimal("4.00"), Decimal("0.20")),
        (Decimal("4.50"), Decimal("0.24")),
        (Decimal("5.00"), Decimal("0.28")),
    ]

    @classmethod
    def calculate_fuel_surcharge_rate(cls, national_diesel_price: Decimal) -> Decimal:
        """Find applicable fuel surcharge percent for current diesel price."""
        selected_rate = Decimal("0.12")
        for price_tier, surcharge_rate in cls.FUEL_SURCHARGE_TABLE:
            if national_diesel_price >= price_tier:
                selected_rate = surcharge_rate
        return selected_rate

    @classmethod
    def rate_freight_shipment(
        cls,
        origin_zip: str,
        destination_zip: str,
        total_weight_lbs: Decimal,
        distance_miles: Decimal,
        is_ftl: bool = False,
        national_diesel_price: Decimal = Decimal("3.85"),
        require_liftgate: bool = False,
        require_inside_delivery: bool = False
    ) -> Dict:
        """
        Calculate freight charges including linehaul, fuel surcharge, and accessorials.
        """
        if distance_miles <= Decimal("0.0") or total_weight_lbs <= Decimal("0.0"):
            raise ValueError("Distance and weight must be positive non-zero.")

        # 1. Base Linehaul
        if is_ftl:
            # FTL Flat mileage rate: $2.40/mile
            base_linehaul = (distance_miles * Decimal("2.40")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            service_mode = "FULL_TRUCKLOAD_FTL"
        else:
            # LTL Hundredweight (CWT) rate: $14.50 / CWT + $0.35/mile factor
            cwt = (total_weight_lbs / Decimal("100.0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            base_linehaul = ((cwt * Decimal("14.50")) + (distance_miles * Decimal("0.35"))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            service_mode = "LESS_THAN_TRUCKLOAD_LTL"

        # 2. Accessorials
        accessorials_total = Decimal("0.0")
        accessorial_details = []

        if require_liftgate:
            fee = Decimal("75.00")
            accessorials_total += fee
            accessorial_details.append({"type": "LIFTGATE_SERVICE", "amount": float(fee)})

        if require_inside_delivery:
            fee = Decimal("95.00")
            accessorials_total += fee
            accessorial_details.append({"type": "INSIDE_DELIVERY", "amount": float(fee)})

        # 3. Fuel Surcharge (FSI)
        fsi_rate = cls.calculate_fuel_surcharge_rate(national_diesel_price)
        fuel_surcharge_amount = (base_linehaul * fsi_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        total_freight_charge = base_linehaul + accessorials_total + fuel_surcharge_amount

        return {
            "origin_zip": origin_zip,
            "destination_zip": destination_zip,
            "service_mode": service_mode,
            "total_weight_lbs": float(total_weight_lbs),
            "distance_miles": float(distance_miles),
            "base_linehaul_charge": float(base_linehaul),
            "fuel_surcharge_rate_percent": float(fsi_rate * Decimal("100.0")),
            "fuel_surcharge_amount": float(fuel_surcharge_amount),
            "accessorial_charges_total": float(accessorials_total),
            "accessorial_breakdown": accessorial_details,
            "total_estimated_freight_charge": float(total_freight_charge)
        }
