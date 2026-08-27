"""
NexERP Asynchronous Event Bus & Dispatcher Subsystem.
Enables loose coupling between ERP business modules via publish-subscribe domain events.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Type
from pydantic import BaseModel

logger = logging.getLogger("nexerp.events")


class DomainEvent(BaseModel):
    """Base class for all ERP domain events."""
    event_name: str
    tenant_id: str
    timestamp: str
    payload: Dict[str, Any]


# Event Handlers Registry
_subscribers: Dict[str, List[Callable[[DomainEvent], Any]]] = {}


def register_event_listener(event_name: str, handler: Callable[[DomainEvent], Any]) -> None:
    """Register a callable subscriber for a named domain event."""
    if event_name not in _subscribers:
        _subscribers[event_name] = []
    _subscribers[event_name].append(handler)
    logger.info(f"Registered event listener for '{event_name}': {handler.__name__}")


async def publish_domain_event(event: DomainEvent) -> None:
    """
    Publish a domain event to all registered listeners asynchronously.
    Catches and logs individual listener exceptions to prevent event failure cascade.
    """
    handlers = _subscribers.get(event.event_name, [])
    if not handlers:
        return

    for handler in handlers:
        try:
            if asyncio.iscoroutinefunction(handler):
                asyncio.create_task(handler(event))
            else:
                handler(event)
        except Exception as exc:
            logger.error(f"Error executing event handler {handler} for {event.event_name}: {exc}", exc_info=True)


# Standard Domain Event Constants
EVENT_JOURNAL_POSTED = "financials.journal.posted"
EVENT_INVOICE_CREATED = "accounts_receivable.invoice.created"
EVENT_PAYMENT_RECEIVED = "accounts_receivable.payment.received"
EVENT_PO_APPROVED = "procurement.po.approved"
EVENT_GRN_RECEIVED = "inventory.grn.received"
EVENT_STOCK_DEPLETED = "inventory.stock.depleted"
EVENT_PRODUCTION_COMPLETED = "manufacturing.production.completed"
EVENT_PAYROLL_FINALIZED = "hr.payroll.finalized"
