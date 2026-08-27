"""
NexERP Quality Control Enums.
"""

from enum import Enum


class InspectionType(str, Enum):
    INCOMING_RECEIPT = "INCOMING_RECEIPT"
    IN_PROCESS = "IN_PROCESS"
    FINAL_DISPATCH = "FINAL_DISPATCH"


class TestType(str, Enum):
    NUMERIC_RANGE = "NUMERIC_RANGE"
    PASS_FAIL = "PASS_FAIL"
    TEXT_MATCH = "TEXT_MATCH"


class InspectionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL = "CONDITIONAL"


class NCRStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    CAPA_PENDING = "CAPA_PENDING"
    CLOSED = "CLOSED"
