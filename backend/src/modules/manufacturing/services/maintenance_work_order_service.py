"""
NexERP Computerized Maintenance Management System (CMMS) & Work Order Engine.
Schedules Preventive Maintenance (PM), monitors machine meter running hours,
calculates spare parts inventory consumption and labor maintenance costs.
"""

from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class MaintenanceWorkOrderService:
    """
    Plant Equipment Preventive Maintenance (PM) & CMMS Work Order Service.
    """

    @classmethod
    def evaluate_pm_schedule_trigger(
        cls,
        machine_id: str,
        machine_name: str,
        current_meter_hours: Decimal,
        last_pm_meter_hours: Decimal,
        meter_interval_hours: Decimal = Decimal("500.0"),
        last_pm_date: Optional[date] = None,
        calendar_interval_days: int = 90
    ) -> Dict:
        """
        Check if machine requires maintenance based on operating hours or calendar elapsed time.
        """
        hours_since_pm = current_meter_hours - last_pm_meter_hours
        hours_due = hours_since_pm >= meter_interval_hours
        hours_remaining = max(Decimal("0.0"), meter_interval_hours - hours_since_pm)

        days_elapsed = (date.today() - last_pm_date).days if last_pm_date else calendar_interval_days
        days_due = days_elapsed >= calendar_interval_days

        is_maintenance_required = hours_due or days_due
        priority = "EMERGENCY" if hours_since_pm >= (meter_interval_hours * Decimal("1.2")) else ("HIGH" if is_maintenance_required else "ROUTINE")

        return {
            "machine_id": machine_id,
            "machine_name": machine_name,
            "current_meter_hours": float(current_meter_hours),
            "hours_since_last_pm": float(hours_since_pm),
            "meter_hours_interval": float(meter_interval_hours),
            "operating_hours_remaining": float(hours_remaining),
            "days_since_last_pm": days_elapsed,
            "calendar_interval_days": calendar_interval_days,
            "is_maintenance_required": is_maintenance_required,
            "work_order_priority": priority,
            "trigger_reason": "METER_HOURS_EXCEEDED" if hours_due else ("CALENDAR_INTERVAL_EXPIRED" if days_due else "IN_TOLERANCE")
        }

    @classmethod
    def calculate_pm_work_order_cost(
        cls,
        labor_hours_spent: Decimal,
        technician_hourly_rate: Decimal,
        spare_parts_consumed: List[Dict]
    ) -> Dict:
        """
        Compute total direct maintenance cost combining labor and consumed MRO spare parts.
        """
        labor_cost = (labor_hours_spent * technician_hourly_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        parts_cost = Decimal("0.0")

        evaluated_parts = []
        for part in spare_parts_consumed:
            qty = Decimal(str(part["quantity"]))
            unit_cost = Decimal(str(part["unit_cost"]))
            total = (qty * unit_cost).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            parts_cost += total
            evaluated_parts.append({
                "part_sku": part.get("part_sku"),
                "description": part.get("description"),
                "quantity": float(qty),
                "unit_cost": float(unit_cost),
                "total_cost": float(total)
            })

        total_pm_cost = labor_cost + parts_cost

        return {
            "labor_hours_spent": float(labor_hours_spent),
            "technician_hourly_rate": float(technician_hourly_rate),
            "total_labor_cost": float(labor_cost),
            "total_parts_cost": float(parts_cost),
            "total_maintenance_cost": float(total_pm_cost),
            "parts_consumed": evaluated_parts
        }
