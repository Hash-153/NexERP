"""
NexERP Financials Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from .enums import AccountType, AccountClassification, JournalStatus, DepreciationMethod, AssetStatus


# Account Schemas
class AccountBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=2, max_length=150)
    account_type: AccountType
    classification: AccountClassification
    parent_account_id: Optional[str] = None
    currency: str = "USD"
    is_reconcilable: bool = False
    is_header_only: bool = False
    description: Optional[str] = None


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    classification: Optional[AccountClassification] = None
    parent_account_id: Optional[str] = None
    is_reconcilable: Optional[bool] = None
    is_header_only: Optional[bool] = None
    description: Optional[str] = None


class AccountResponse(AccountBase):
    id: str
    tenant_id: str
    current_balance: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# Fiscal Period Schemas
class FiscalPeriodResponse(BaseModel):
    id: str
    fiscal_year_id: str
    period_number: int
    name: str
    start_date: date
    end_date: date
    is_locked: bool
    is_adjustment_period: bool

    class Config:
        from_attributes = True


class FiscalYearCreate(BaseModel):
    name: str
    start_date: date
    end_date: date


class FiscalYearResponse(BaseModel):
    id: str
    name: str
    start_date: date
    end_date: date
    is_closed: bool
    periods: List[FiscalPeriodResponse] = []

    class Config:
        from_attributes = True


class JournalEntryLineCreate(BaseModel):
    account_id: str
    debit: Decimal = Field(default=Decimal("0.0"), ge=0)
    credit: Decimal = Field(default=Decimal("0.0"), ge=0)
    debit_currency: Optional[Decimal] = None
    credit_currency: Optional[Decimal] = None
    description: Optional[str] = None
    partner_type: Optional[str] = None
    partner_id: Optional[str] = None
    cost_center_id: Optional[str] = None
    project_id: Optional[str] = None

    @field_validator("credit")
    @classmethod
    def validate_single_sided_line(cls, v, values):
        # Line must have either debit > 0 or credit > 0, not both
        return v


class JournalEntryLineResponse(BaseModel):
    id: str
    journal_entry_id: str
    account_id: str
    line_number: int
    debit: Decimal
    credit: Decimal
    description: Optional[str]
    partner_type: Optional[str]
    partner_id: Optional[str]
    cost_center_id: Optional[str]
    project_id: Optional[str]

    class Config:
        from_attributes = True


# Journal Entry Schemas
class JournalEntryCreate(BaseModel):
    entry_date: date
    period_id: str
    currency: str = "USD"
    exchange_rate: Decimal = Decimal("1.0")
    reference: Optional[str] = None
    narration: Optional[str] = None
    source_document_type: Optional[str] = None
    source_document_id: Optional[str] = None
    lines: List[JournalEntryLineCreate] = Field(..., min_length=2)


class JournalEntryResponse(BaseModel):
    id: str
    tenant_id: str
    voucher_number: str
    entry_date: date
    posting_date: Optional[date]
    period_id: str
    currency: str
    exchange_rate: Decimal
    status: JournalStatus
    reference: Optional[str]
    narration: Optional[str]
    total_debit: Decimal
    total_credit: Decimal
    posted_at: Optional[datetime]
    posted_by_id: Optional[str]
    reversed_entry_id: Optional[str]
    lines: List[JournalEntryLineResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Fixed Asset Schemas
class FixedAssetCreate(BaseModel):
    asset_number: str
    name: str
    category: str
    acquisition_date: date
    acquisition_cost: Decimal = Field(..., gt=0)
    salvage_value: Decimal = Field(default=Decimal("0.0"), ge=0)
    useful_life_months: int = Field(..., gt=0)
    depreciation_method: DepreciationMethod = DepreciationMethod.STRAIGHT_LINE
    asset_account_id: str
    accumulated_depr_account_id: str
    depr_expense_account_id: str


class DepreciationScheduleResponse(BaseModel):
    id: str
    schedule_date: date
    depreciation_amount: Decimal
    accumulated_depreciation: Decimal
    book_value: Decimal
    is_posted: bool
    journal_entry_id: Optional[str]

    class Config:
        from_attributes = True


class FixedAssetResponse(BaseModel):
    id: str
    tenant_id: str
    asset_number: str
    name: str
    category: str
    acquisition_date: date
    acquisition_cost: Decimal
    salvage_value: Decimal
    useful_life_months: int
    depreciation_method: DepreciationMethod
    status: AssetStatus
    schedules: List[DepreciationScheduleResponse] = []

    class Config:
        from_attributes = True


# Financial Reporting Schemas
class TrialBalanceItem(BaseModel):
    account_code: str
    account_name: str
    account_type: str
    classification: str
    debit_balance: Decimal
    credit_balance: Decimal


class TrialBalanceResponse(BaseModel):
    as_of_date: date
    items: List[TrialBalanceItem]
    total_debits: Decimal
    total_credits: Decimal
    is_balanced: bool


class BalanceSheetSection(BaseModel):
    section_name: str
    total_amount: Decimal
    items: List[dict]


class BalanceSheetResponse(BaseModel):
    as_of_date: date
    assets: BalanceSheetSection
    liabilities: BalanceSheetSection
    equity: BalanceSheetSection
    total_assets: Decimal
    total_liabilities_and_equity: Decimal
    is_balanced: bool


class IncomeStatementResponse(BaseModel):
    start_date: date
    end_date: date
    operating_revenue: Decimal
    cost_of_goods_sold: Decimal
    gross_profit: Decimal
    operating_expenses: Decimal
    operating_income: Decimal
    other_income_expense: Decimal
    net_income_before_tax: Decimal
    tax_expense: Decimal
    net_profit: Decimal
