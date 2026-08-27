"""
NexERP Accounts Payable Enums.
"""

from enum import Enum


class BillStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    CANCELLED = "CANCELLED"


class PaymentMethod(str, Enum):
    WIRE_TRANSFER = "WIRE_TRANSFER"
    CHECK = "CHECK"
    ACH = "ACH"
    CREDIT_CARD = "CREDIT_CARD"
    CASH = "CASH"


class PaymentRunStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"
