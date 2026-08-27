"""Shared assertions for stable API and accounting test contracts."""

from decimal import Decimal
from typing import Any, Iterable, Mapping


def assert_json_keys(payload: Mapping[str, Any], required: Iterable[str], optional: Iterable[str] = ()) -> None:
    """Assert required response keys while documenting permitted optional keys."""
    missing = set(required) - set(payload)
    assert not missing, f"Response is missing keys: {sorted(missing)}"
    allowed = set(required) | set(optional)
    unexpected = set(payload) - allowed
    assert not unexpected, f"Response contains unexpected keys: {sorted(unexpected)}"


def assert_money(actual: Any, expected: str) -> None:
    """Compare numeric API values as Decimal to avoid float comparison errors."""
    assert Decimal(str(actual)).quantize(Decimal("0.01")) == Decimal(expected).quantize(Decimal("0.01"))


def assert_error_contract(payload: Mapping[str, Any], error_code: str, status_code: int) -> None:
    """Validate the standard NexERP domain exception response shape."""
    assert payload.get("error_code") == error_code
    assert payload.get("status_code") == status_code
    assert isinstance(payload.get("message"), str)
    assert isinstance(payload.get("details"), dict)


def assert_tenant_boundary(records: Iterable[Mapping[str, Any]], tenant_id: str) -> None:
    """Ensure every returned record belongs to the authenticated tenant."""
    for record in records:
        assert record.get("tenant_id") == tenant_id


def assert_sorted_by(records: list[Mapping[str, Any]], field: str, reverse: bool = False) -> None:
    """Assert deterministic API ordering for list endpoints."""
    values = [record[field] for record in records]
    assert values == sorted(values, reverse=reverse)


def assert_transition(current: str, target: str, transitions: Mapping[str, set[str]]) -> None:
    """Assert a workflow transition is represented in its state machine."""
    assert target == current or target in transitions.get(current, set())
