"""
NexERP Financials & General Ledger Database Models.
Adheres to GAAP and IFRS double-entry accounting standards with hierarchical Chart of Accounts,
immutable posted journal vouchers, multi-currency ledger balances, fiscal calendar locking, and fixed asset schedules.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Account(Base):
    """
    General Ledger Chart of Accounts (COA) entry.
    """
    __tablename__ = "fin_accounts"

    code = Column(String(50), nullable=False, index=True, doc="Unique account code, e.g. '10100', '40000'")
    name = Column(String(150), nullable=False, doc="Account title, e.g. 'Operating Bank Account'")
    account_type = Column(String(30), nullable=False, index=True, doc="ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE")
    classification = Column(String(50), nullable=False, doc="Current Asset, Fixed Asset, Current Liability, etc.")
    
    parent_account_id = Column(String(36), ForeignKey("fin_accounts.id", ondelete="SET NULL"), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    
    is_reconcilable = Column(Boolean, default=False, nullable=False, doc="Can be matched against bank statements or AR/AP")
    is_header_only = Column(Boolean, default=False, nullable=False, doc="Group header account, cannot accept direct journal lines")
    
    current_balance = Column(Numeric(18, 4), default=0.0, nullable=False, doc="Cached debit/credit running balance")
    description = Column(Text, nullable=True)

    parent = relationship("Account", remote_side="Account.id", backref="children")
    journal_lines = relationship("JournalEntryLine", back_populates="account")

    __table_args__ = (
        Index("ix_fin_account_tenant_code", "tenant_id", "code", unique=True),
    )


class FiscalYear(Base):
    """
    Financial reporting fiscal year container.
    """
    __tablename__ = "fin_fiscal_years"

    name = Column(String(50), nullable=False, doc="e.g. 'FY 2026'")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_closed = Column(Boolean, default=False, nullable=False)

    periods = relationship("FiscalPeriod", back_populates="fiscal_year", cascade="all, delete-orphan")


class FiscalPeriod(Base):
    """
    Accounting period (monthly/quarterly) for closing and ledger locking.
    """
    __tablename__ = "fin_fiscal_periods"

    fiscal_year_id = Column(String(36), ForeignKey("fin_fiscal_years.id", ondelete="CASCADE"), nullable=False)
    period_number = Column(Integer, nullable=False, doc="1 through 12 (or 13 for year-end adjustments)")
    name = Column(String(50), nullable=False, doc="e.g. 'January 2026' or '2026-P01'")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False, doc="Locked periods reject new journal postings")
    is_adjustment_period = Column(Boolean, default=False, nullable=False)

    fiscal_year = relationship("FiscalYear", back_populates="periods")
    journal_entries = relationship("JournalEntry", back_populates="period")


class JournalEntry(Base):
    """
    Double-entry journal voucher representing a financial transaction.
    """
    __tablename__ = "fin_journal_entries"

    voucher_number = Column(String(50), nullable=False, index=True, doc="e.g. 'JV-2026-0001'")
    entry_date = Column(Date, nullable=False, index=True)
    posting_date = Column(Date, nullable=True)
    period_id = Column(String(36), ForeignKey("fin_fiscal_periods.id"), nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, index=True, doc="DRAFT, SUBMITTED, POSTED, REVERSED")
    source_document_type = Column(String(50), nullable=True, doc="VendorBill, SalesInvoice, PayrollRun, etc.")
    source_document_id = Column(String(36), nullable=True, index=True)
    
    reference = Column(String(100), nullable=True, doc="External invoice or check reference")
    narration = Column(Text, nullable=True, doc="Explanation of business purpose")
    
    total_debit = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_credit = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    posted_at = Column(DateTime(timezone=True), nullable=True)
    posted_by_id = Column(String(36), nullable=True)
    reversed_entry_id = Column(String(36), nullable=True, doc="Points to reversal voucher if reversed")

    period = relationship("FiscalPeriod", back_populates="journal_entries")
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_fin_journal_tenant_voucher", "tenant_id", "voucher_number", unique=True),
    )


class JournalEntryLine(Base):
    """
    Individual debit or credit posting row within a journal voucher.
    """
    __tablename__ = "fin_journal_entry_lines"

    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id", ondelete="CASCADE"), nullable=False)
    account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    debit = Column(Numeric(18, 4), default=0.0, nullable=False)
    credit = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    debit_currency = Column(Numeric(18, 4), default=0.0, nullable=False)
    credit_currency = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    description = Column(String(255), nullable=True)
    
    # Subledger / Analytical Dimensions
    partner_type = Column(String(30), nullable=True, doc="CUSTOMER, VENDOR, EMPLOYEE")
    partner_id = Column(String(36), nullable=True, index=True)
    cost_center_id = Column(String(36), nullable=True, index=True)
    project_id = Column(String(36), nullable=True, index=True)

    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account", back_populates="journal_lines")


class TaxCategory(Base):
    """
    Tax classification grouping (e.g. Standard VAT, Reduced Rate, Exempt, Reverse Charge).
    """
    __tablename__ = "fin_tax_categories"

    name = Column(String(100), nullable=False)
    code = Column(String(30), nullable=False)
    description = Column(Text, nullable=True)

    tax_rates = relationship("TaxRate", back_populates="category", cascade="all, delete-orphan")


class TaxRate(Base):
    """
    Specific statutory tax rate definition with linked GL settlement account.
    """
    __tablename__ = "fin_tax_rates"

    category_id = Column(String(36), ForeignKey("fin_tax_categories.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(30), nullable=False)
    name = Column(String(100), nullable=False)
    rate_percent = Column(Numeric(7, 4), nullable=False, doc="e.g. 20.0000 for 20% VAT, 8.8750 for NY Sales Tax")
    
    sales_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="Tax liability output account")
    purchase_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="Tax asset input account")
    
    is_recoverable = Column(Boolean, default=True, nullable=False)
    is_compound = Column(Boolean, default=False, nullable=False)

    category = relationship("TaxCategory", back_populates="tax_rates")


class FixedAsset(Base):
    """
    Capitalized plant, property, and equipment (PPE) subject to depreciation.
    """
    __tablename__ = "fin_fixed_assets"

    asset_number = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False, doc="Machinery, IT Equipment, Vehicles, Buildings")
    
    acquisition_date = Column(Date, nullable=False)
    acquisition_cost = Column(Numeric(18, 4), nullable=False)
    salvage_value = Column(Numeric(18, 4), default=0.0, nullable=False)
    useful_life_months = Column(Integer, nullable=False)
    depreciation_method = Column(String(30), default="STRAIGHT_LINE", nullable=False, doc="STRAIGHT_LINE, DOUBLE_DECLINING")
    
    asset_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    accumulated_depr_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    depr_expense_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    
    status = Column(String(30), default="ACTIVE", nullable=False, doc="ACTIVE, FULLY_DEPRECIATED, DISPOSED")
    disposal_date = Column(Date, nullable=True)
    disposal_amount = Column(Numeric(18, 4), nullable=True)

    schedules = relationship("DepreciationSchedule", back_populates="asset", cascade="all, delete-orphan")


class DepreciationSchedule(Base):
    """
    Monthly amortization table row for a capitalized fixed asset.
    """
    __tablename__ = "fin_depreciation_schedules"

    asset_id = Column(String(36), ForeignKey("fin_fixed_assets.id", ondelete="CASCADE"), nullable=False)
    period_id = Column(String(36), ForeignKey("fin_fiscal_periods.id"), nullable=True)
    schedule_date = Column(Date, nullable=False)
    
    depreciation_amount = Column(Numeric(18, 4), nullable=False)
    accumulated_depreciation = Column(Numeric(18, 4), nullable=False)
    book_value = Column(Numeric(18, 4), nullable=False)
    
    is_posted = Column(Boolean, default=False, nullable=False)
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)

    asset = relationship("FixedAsset", back_populates="schedules")


class ExchangeRate(Base):
    """
    Foreign exchange spot rate conversion entry.
    """
    __tablename__ = "fin_exchange_rates"

    from_currency = Column(String(3), nullable=False, index=True)
    to_currency = Column(String(3), nullable=False, index=True)
    rate = Column(Numeric(18, 6), nullable=False)
    effective_date = Column(Date, nullable=False, index=True)


class CostCenter(Base):
    """
    Departmental or functional cost center for management accounting and variance reporting.
    """
    __tablename__ = "fin_cost_centers"

    code = Column(String(30), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    manager_id = Column(String(36), nullable=True)
    parent_cost_center_id = Column(String(36), ForeignKey("fin_cost_centers.id", ondelete="SET NULL"), nullable=True)
