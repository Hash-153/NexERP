"""
NexERP Sales Enums.
"""

from enum import Enum


class LeadStage(str, Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    WON = "WON"
    LOST = "LOST"


class QuoteStatus(str, Enum):
    DRAFT = "DRAFT"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class SalesOrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    PROCESSING = "PROCESSING"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    FULFILLED = "FULFILLED"
    CANCELLED = "CANCELLED"


class DeliveryStatus(str, Enum):
    PICKED = "PICKED"
    PACKED = "PACKED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
