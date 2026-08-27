"""
NexERP Manufacturing Enums.
"""

from enum import Enum


class WorkCenterType(str, Enum):
    MACHINE = "MACHINE"
    LABOR = "LABOR"
    ASSEMBLY = "ASSEMBLY"
    OUTSOURCED = "OUTSOURCED"


class ProductionOrderStatus(str, Enum):
    PLANNED = "PLANNED"
    RELEASED = "RELEASED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class JobCardStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class MRPOrderType(str, Enum):
    PURCHASE = "PURCHASE"
    PRODUCTION = "PRODUCTION"
