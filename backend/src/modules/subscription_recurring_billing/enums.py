"""
Subscription & Recurring Billing Enums.
"""
import enum

class BillingFrequency(str, enum.Enum):
    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    ANNUAL_UPFRONT = "ANNUAL_UPFRONT"
    MULTI_YEAR_PREPAID = "MULTI_YEAR_PREPAID"

class SubscriptionLifecycleState(str, enum.Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PENDING_UPGRADE = "PENDING_UPGRADE"
    SUSPENDED_DUNNING = "SUSPENDED_DUNNING"
    CANCELLED = "CANCELLED"
    CHURNED = "CHURNED"
