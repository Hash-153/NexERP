"""
NexERP Field Service Management (FSM) & SLA Dispatching Engine.
Manages:
- Service Level Agreement (SLA) Response & Resolution Time Clocks (e.g. 4-hour Gold SLA)
- Field Technician Dispatch assignment by geography and skill certification
- On-site replacement parts consumption & billable labor hours accounting.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class FieldServiceDispatchService:
    """
    Field Service Management & SLA Dispatch Service.
    """

    SLA_RESOLUTION_WINDOWS_HOURS = {
        "PLATINUM": 4,
        "GOLD": 8,
        "SILVER": 24,
        "STANDARD": 48
    }

    @classmethod
    def dispatch_service_ticket(
        cls,
        ticket_id: str,
        customer_name: str,
        service_address: str,
        sla_tier: str,
        created_at: datetime,
        technician_id: str,
        technician_name: str,
        estimated_labor_hours: Decimal,
        hourly_rate_usd: Decimal = Decimal("125.00")
    ) -> Dict:
        """
        Create field work order, compute SLA breach deadline, and quote labor charge.
        """
        sla = sla_tier.upper()
        window_hours = cls.SLA_RESOLUTION_WINDOWS_HOURS.get(sla, 48)
        sla_deadline = created_at + timedelta(hours=window_hours)

        labor_total = (estimated_labor_hours * hourly_rate_usd).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "service_ticket_id": ticket_id,
            "customer_name": customer_name,
            "service_address": service_address,
            "sla_tier": sla,
            "sla_window_hours": window_hours,
            "ticket_created_at": created_at.isoformat(),
            "sla_deadline": sla_deadline.isoformat(),
            "assigned_technician_id": technician_id,
            "assigned_technician_name": technician_name,
            "estimated_labor_hours": float(estimated_labor_hours),
            "hourly_labor_rate": float(hourly_rate_usd),
            "total_estimated_labor_cost": float(labor_total),
            "dispatch_status": "DISPATCHED_IN_TRANSIT"
        }
