"""
NexERP Projects Enums.
"""

from enum import Enum


class BillingType(str, Enum):
    TIME_AND_MATERIALS = "TIME_AND_MATERIALS"
    FIXED_PRICE = "FIXED_PRICE"


class ProjectStatus(str, Enum):
    PLANNED = "PLANNED"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"


class TimesheetStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
