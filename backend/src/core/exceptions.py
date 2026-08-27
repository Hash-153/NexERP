"""
NexERP Domain Exceptions & Standard Error Hierarchy.
Provides structured, semantic exceptions mapped to appropriate HTTP status codes and error responses.
"""

from typing import Any, Dict, Optional


class NexERPBaseException(Exception):
    """Root base exception for all NexERP domain errors."""
    default_message = "An unexpected error occurred in the enterprise system."
    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None
    ):
        self.message = message or self.default_message
        self.details = details or {}
        if status_code:
            self.status_code = status_code
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code
        }


class EntityNotFoundError(NexERPBaseException):
    """Raised when a requested resource is not found in database."""
    default_message = "Requested entity was not found."
    status_code = 404
    error_code = "ENTITY_NOT_FOUND"


class EntityAlreadyExistsError(NexERPBaseException):
    """Raised when attempting to create an entity that already exists."""
    default_message = "Entity with the given unique identifier already exists."
    status_code = 409
    error_code = "ENTITY_ALREADY_EXISTS"


class BusinessRuleViolationError(NexERPBaseException):
    """Raised when an operation violates an explicit business rule."""
    default_message = "Operation violates a core enterprise business rule."
    status_code = 422
    error_code = "BUSINESS_RULE_VIOLATION"


class UnauthorizedError(NexERPBaseException):
    """Raised when authentication credentials are missing or invalid."""
    default_message = "Authentication credentials were not provided or are invalid."
    status_code = 401
    error_code = "UNAUTHORIZED"


class PermissionDeniedError(NexERPBaseException):
    """Raised when authenticated user lacks the required RBAC/ABAC permissions."""
    default_message = "You do not have sufficient permissions to perform this action."
    status_code = 403
    error_code = "PERMISSION_DENIED"


# ==============================================================================
# Financials & Accounting Specific Exceptions
# ==============================================================================

class UnbalancedJournalEntryError(BusinessRuleViolationError):
    """Raised when total debits do not equal total credits in a journal voucher."""
    default_message = "General ledger journal entry must balance (Debits must equal Credits)."
    error_code = "UNBALANCED_JOURNAL_ENTRY"


class AccountingPeriodClosedError(BusinessRuleViolationError):
    """Raised when attempting to post a transaction to a closed or locked fiscal period."""
    default_message = "Transactions cannot be posted to a closed or locked fiscal accounting period."
    error_code = "FISCAL_PERIOD_CLOSED"


class AccountTypeMismatchError(BusinessRuleViolationError):
    """Raised when an account of incorrect classification is selected."""
    default_message = "The selected account type is incompatible with this transaction."
    error_code = "ACCOUNT_TYPE_MISMATCH"


# ==============================================================================
# Inventory & Warehouse Specific Exceptions
# ==============================================================================

class InsufficientStockError(BusinessRuleViolationError):
    """Raised when stock movement exceeds available unreserved inventory."""
    default_message = "Insufficient stock available in specified warehouse bin."
    error_code = "INSUFFICIENT_STOCK"


class NegativeStockProhibitedError(BusinessRuleViolationError):
    """Raised when an inventory operation would drive physical inventory below zero."""
    default_message = "Negative stock balance is strictly prohibited by warehouse policy."
    error_code = "NEGATIVE_STOCK_PROHIBITED"


class StockValuationError(BusinessRuleViolationError):
    """Raised when FIFO queue depletion or cost calculation fails."""
    default_message = "Inventory valuation layer computation encountered an inconsistency."
    error_code = "STOCK_VALUATION_ERROR"


# ==============================================================================
# Procurement & SCM Exceptions
# ==============================================================================

class ThreeWayMatchToleranceError(BusinessRuleViolationError):
    """Raised when PO, GRN, and Vendor Bill quantities or unit prices exceed tolerance threshold."""
    default_message = "3-Way Match validation failed due to price or quantity variance exceeding tolerance."
    error_code = "THREE_WAY_MATCH_TOLERANCE_EXCEEDED"


# ==============================================================================
# Sales & Credit Control Exceptions
# ==============================================================================

class CreditLimitExceededError(BusinessRuleViolationError):
    """Raised when a customer sales order pushes outstanding receivables beyond approved credit limit."""
    default_message = "Customer credit limit has been exceeded. Approval or payment required."
    error_code = "CREDIT_LIMIT_EXCEEDED"


# ==============================================================================
# Manufacturing & MRP Exceptions
# ==============================================================================

class BOMRecursionError(BusinessRuleViolationError):
    """Raised when a recursive circular dependency is detected in a multi-level BOM."""
    default_message = "Circular reference detected in Bill of Materials hierarchy."
    error_code = "BOM_CIRCULAR_DEPENDENCY"


class WorkCenterOverloadError(BusinessRuleViolationError):
    """Raised when scheduled production exceeds finite capacity of work center."""
    default_message = "Work center finite capacity exceeded for scheduled time window."
    error_code = "WORK_CENTER_OVERLOAD"


# ==============================================================================
# Dynamic Workflow Exceptions
# ==============================================================================

class WorkflowTransitionError(BusinessRuleViolationError):
    """Raised when an invalid state transition is requested."""
    default_message = "Invalid state transition for the current document workflow status."
    error_code = "INVALID_WORKFLOW_TRANSITION"


class ApprovalRequiredError(BusinessRuleViolationError):
    """Raised when a document requires formal managerial approval prior to posting."""
    default_message = "Document requires formal tier approval before it can be finalized."
    error_code = "APPROVAL_REQUIRED"


# ==============================================================================
# Human Resources & Payroll Exceptions
# ==============================================================================

class PayrollCalculationError(BusinessRuleViolationError):
    """Raised when salary computation encounters invalid structure or negative net pay."""
    default_message = "Error computing payroll structure: net pay cannot be negative."
    error_code = "PAYROLL_CALCULATION_ERROR"


class InsufficientLeaveBalanceError(BusinessRuleViolationError):
    """Raised when leave request exceeds employee accrued balance."""
    default_message = "Insufficient accrued leave balance for requested date range."
    error_code = "INSUFFICIENT_LEAVE_BALANCE"
