"""
NexERP Procurement Enums.
"""

from enum import Enum


class RequisitionStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ORDERED = "ORDERED"


class RFQStatus(str, Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    EVALUATED = "EVALUATED"
    CLOSED = "CLOSED"


class POStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ISSUED = "ISSUED"
    PARTIALLY_RECEIVED = "PARTIALLY_RECEIVED"
    RECEIVED = "RECEIVED"
    CANCELLED = "CANCELLED"


class GRNStatus(str, Enum):
    RECEIVED = "RECEIVED"
    QC_HOLD = "QC_HOLD"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
