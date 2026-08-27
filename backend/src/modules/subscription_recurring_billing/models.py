"""
Subscription Billing Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class CustomerSubscriptionContract(Base):
    """Recurring revenue subscription contract."""
    __tablename__ = "sub_contracts"

    customer_account_id = Column(String(36), nullable=False, index=True)
    plan_name = Column(String(100), nullable=False)
    billing_frequency = Column(String(30), default="ANNUAL_UPFRONT", nullable=False)
    status = Column(String(30), default="ACTIVE", nullable=False)
    
    contract_start_date = Column(Date, nullable=False)
    contract_end_date = Column(Date, nullable=False)
    annual_recurring_revenue_arr = Column(Numeric(14, 4), nullable=False)
    monthly_recurring_revenue_mrr = Column(Numeric(14, 4), nullable=False)
    
    seat_count = Column(Integer, default=100, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    unearned_deferred_revenue_balance = Column(Numeric(14, 4), default=0.0, nullable=False)


class RevenueRecognitionScheduleASC606(Base):
    """ASC 606 monthly revenue recognition amortization schedule."""
    __tablename__ = "sub_revenue_schedules"

    subscription_id = Column(String(36), ForeignKey("sub_contracts.id", ondelete="CASCADE"), nullable=False)
    fiscal_period = Column(String(10), nullable=False)  # '2026-03'
    recognized_amount = Column(Numeric(14, 4), nullable=False)
    deferred_ending_balance = Column(Numeric(14, 4), nullable=False)
    is_posted = Column(Boolean, default=False, nullable=False)
