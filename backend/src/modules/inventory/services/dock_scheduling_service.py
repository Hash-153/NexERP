"""
NexERP Warehouse Dock Appointment & Yard Management Engine.
Manages:
- Inbound Receiving Dock Bay Reservations
- Outbound Staging & Cross-Dock Bay Appointments
- Carrier Turnaround / Detention Time Tracking.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional


class DockSchedulingService:
    """
    Dock Appointment & Yard Management Service.
    """

    @classmethod
    def schedule_dock_appointment(
        cls,
        carrier_name: str,
        shipment_type: str,
        trailer_number: str,
        requested_start_time: datetime,
        duration_minutes: int,
        active_dock_doors: List[Dict]
    ) -> Dict:
        """
        Assign an available warehouse dock door matching the shipment type without scheduling collisions.
        """
        target_end_time = requested_start_time + timedelta(minutes=duration_minutes)

        # Filter doors compatible with shipment_type (INBOUND or OUTBOUND)
        available_door = None
        for door in active_dock_doors:
            if door.get("door_type", "UNIVERSAL") not in [shipment_type.upper(), "UNIVERSAL"]:
                continue

            # Check if door has existing conflicting bookings
            existing_bookings = door.get("bookings", [])
            has_conflict = False
            for b in existing_bookings:
                b_start = b["start_time"]
                b_end = b["end_time"]
                if not (target_end_time <= b_start or requested_start_time >= b_end):
                    has_conflict = True
                    break

            if not has_conflict:
                available_door = door
                break

        if not available_door:
            return {
                "is_scheduled": False,
                "assigned_door": None,
                "reason": "All compatible dock doors are occupied during the requested time window."
            }

        return {
            "is_scheduled": True,
            "appointment_id": f"DOCK-APT-{requested_start_time.strftime('%Y%m%d%H%M')}",
            "carrier_name": carrier_name,
            "shipment_type": shipment_type.upper(),
            "trailer_number": trailer_number,
            "assigned_door_id": available_door["id"],
            "assigned_door_number": available_door["door_number"],
            "start_time": requested_start_time.isoformat(),
            "end_time": target_end_time.isoformat(),
            "duration_minutes": duration_minutes,
            "status": "CONFIRMED"
        }
