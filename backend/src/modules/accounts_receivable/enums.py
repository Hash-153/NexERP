"""
NexERP Accounts Receivable Enums.
"""

from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    POSTED = "POSTED"
    PAID = "PAID"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    CANCELLED = "CANCELLED"


class ReceiptStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


class DunningLevel(int, Enum):
    CURRENT = 0
    LEVEL_1_REMINDER = 1
    LEVEL_2_WARNING = 2
    LEVEL_3_DEMAND = 3
    LEGAL_ACTION = 4
