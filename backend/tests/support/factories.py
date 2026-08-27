"""Deterministic payload factories for service, planning, and API tests."""

from datetime import date, datetime, timezone
from decimal import Decimal
from itertools import count
from typing import Any, Dict, Optional

_sequence = count(1)


def _number(prefix: str) -> str:
    return f"{prefix}-{next(_sequence):05d}"


def make_contract_payload(**overrides: Any) -> Dict[str, Any]:
    """Create a valid service contract payload with overridable fields."""
    payload = {
        "contract_number": _number("SVC"),
        "name": "Factory support agreement",
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
        "contract_type": "TIME_AND_MATERIALS",
        "currency": "USD",
        "value": Decimal("25000"),
        "response_hours": Decimal("4"),
        "resolution_hours": Decimal("48"),
        "included_hours": Decimal("100"),
    }
    payload.update(overrides)
    return payload


def make_ticket_payload(**overrides: Any) -> Dict[str, Any]:
    """Create a valid support ticket payload."""
    payload = {
        "subject": "Production equipment requires attention",
        "description": "The equipment is operating outside its expected parameters.",
        "channel": "PORTAL",
        "priority": "NORMAL",
        "billable": True,
        "estimated_hours": Decimal("2"),
    }
    payload.update(overrides)
    return payload


def make_forecast_payload(**overrides: Any) -> Dict[str, Any]:
    """Create a valid demand forecast payload."""
    payload = {
        "item_id": "item-test-001",
        "warehouse_id": "warehouse-test-001",
        "period_start": date(2026, 9, 1),
        "period_end": date(2026, 9, 30),
        "forecast_quantity": Decimal("100"),
        "baseline_quantity": Decimal("80"),
        "promotion_quantity": Decimal("20"),
        "confidence_percent": Decimal("85"),
        "method": "MOVING_AVERAGE",
    }
    payload.update(overrides)
    return payload


def make_timestamp(day: int = 1, hour: int = 8) -> datetime:
    """Return a stable UTC timestamp for time-based tests."""
    return datetime(2026, 1, day, hour, tzinfo=timezone.utc)


def make_decimal_sequence(start: str, step: str, length: int) -> list[Decimal]:
    """Generate predictable Decimal values without floating-point drift."""
    current = Decimal(start)
    increment = Decimal(step)
    values = []
    for _ in range(length):
        values.append(current)
        current += increment
    return values
