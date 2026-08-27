"""
Strategic Budgeting Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class StrategicBudgetPlan(Base):
    """Annual or multi-year corporate budget master plan."""
    __tablename__ = "bgt_plans"

    fiscal_year = Column(Integer, nullable=False, index=True)
    plan_name = Column(String(150), nullable=False)
    version_type = Column(String(40), default="ORIGINAL_APPROVED", nullable=False)
    status = Column(String(30), default="DRAFT_PREPARATION", nullable=False)
    
    total_revenue_budget = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_opex_budget = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_capex_budget = Column(Numeric(18, 4), default=0.0, nullable=False)
    net_ebitda_budget = Column(Numeric(18, 4), default=0.0, nullable=False)
    target_ebitda_margin_pct = Column(Numeric(5, 2), default=22.5, nullable=False)

    cost_center_lines = relationship("CostCenterBudgetLine", back_populates="plan", cascade="all, delete-orphan")


class CostCenterBudgetLine(Base):
    """Cost-center level monthly budget allocation."""
    __tablename__ = "bgt_cost_center_lines"

    plan_id = Column(String(36), ForeignKey("bgt_plans.id", ondelete="CASCADE"), nullable=False)
    cost_center_code = Column(String(50), nullable=False, index=True)
    cost_center_name = Column(String(150), nullable=False)
    expense_type = Column(String(40), default="OPEX_HEADCOUNT", nullable=False)
    
    month_01_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_02_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_03_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_04_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_05_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_06_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_07_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_08_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_09_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_10_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_11_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    month_12_amt = Column(Numeric(14, 4), default=0.0, nullable=False)
    total_annual_allocation = Column(Numeric(18, 4), default=0.0, nullable=False)

    plan = relationship("StrategicBudgetPlan", back_populates="cost_center_lines")
