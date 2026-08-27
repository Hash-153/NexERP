"""
NexERP Financials & General Ledger REST API Router.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser, RequirePermission
from backend.src.modules.financials.models import Account, JournalEntry
from backend.src.modules.financials.schemas import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    FiscalYearCreate,
    FiscalYearResponse,
    FiscalPeriodResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    FixedAssetCreate,
    FixedAssetResponse,
    TrialBalanceResponse,
    BalanceSheetResponse,
    IncomeStatementResponse
)
from backend.src.modules.financials.services import (
    GeneralLedgerService,
    FiscalPeriodService,
    FixedAssetService,
    FinancialReportingService
)

router = APIRouter(prefix="/financials", tags=["General Ledger & Financial Accounting"])


# ==============================================================================
# Chart of Accounts (COA)
# ==============================================================================

@router.get("/accounts", response_model=List[AccountResponse])
async def list_chart_of_accounts(
    current_user: CurrentUser = Depends(RequirePermission("financials:account:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Retrieve full hierarchical Chart of Accounts for the tenant."""
    query = (
        select(Account)
        .where(Account.tenant_id == current_user.tenant_id, Account.is_deleted == False)
        .order_by(Account.code.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    current_user: CurrentUser = Depends(RequirePermission("financials:account:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new general ledger account in the Chart of Accounts."""
    account = Account(
        tenant_id=current_user.tenant_id,
        code=payload.code.strip(),
        name=payload.name.strip(),
        account_type=payload.account_type.value,
        classification=payload.classification.value,
        parent_account_id=payload.parent_account_id,
        currency=payload.currency.upper(),
        is_reconcilable=payload.is_reconcilable,
        is_header_only=payload.is_header_only,
        description=payload.description
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


# ==============================================================================
# Journal Entries & Vouchers
# ==============================================================================

@router.get("/journals", response_model=List[JournalEntryResponse])
async def list_journal_entries(
    skip: int = 0,
    limit: int = 50,
    status_filter: Optional[str] = None,
    current_user: CurrentUser = Depends(RequirePermission("financials:journal:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List journal vouchers with filtering by posting status."""
    query = (
        select(JournalEntry)
        .where(JournalEntry.tenant_id == current_user.tenant_id, JournalEntry.is_deleted == False)
        .options(selectinload(JournalEntry.lines))
        .order_by(JournalEntry.entry_date.desc(), JournalEntry.voucher_number.desc())
        .offset(skip)
        .limit(limit)
    )
    if status_filter:
        query = query.where(JournalEntry.status == status_filter.upper())

    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/journals", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_voucher(
    payload: JournalEntryCreate,
    current_user: CurrentUser = Depends(RequirePermission("financials:journal:create")),
    db: AsyncSession = Depends(get_db_session)
):
    """Create and validate a balanced double-entry journal voucher."""
    return await GeneralLedgerService.create_journal_entry(
        db=db,
        tenant_id=current_user.tenant_id,
        payload=payload,
        user_id=current_user.id
    )


@router.post("/journals/{journal_id}/post", response_model=JournalEntryResponse)
async def post_journal_voucher(
    journal_id: str,
    current_user: CurrentUser = Depends(RequirePermission("financials:journal:post")),
    db: AsyncSession = Depends(get_db_session)
):
    """Post draft journal voucher to general ledger, updating account running balances."""
    return await GeneralLedgerService.post_journal_entry(
        db=db,
        tenant_id=current_user.tenant_id,
        journal_id=journal_id,
        user_id=current_user.id
    )


@router.post("/journals/{journal_id}/reverse", response_model=JournalEntryResponse)
async def reverse_journal_voucher(
    journal_id: str,
    reversal_date: date = Query(default_factory=date.today),
    reason: str = Query(..., min_length=5),
    current_user: CurrentUser = Depends(RequirePermission("financials:journal:post")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate and post an exact inverse reversal voucher to void a posted entry."""
    return await GeneralLedgerService.reverse_journal_entry(
        db=db,
        tenant_id=current_user.tenant_id,
        journal_id=journal_id,
        reversal_date=reversal_date,
        reason=reason,
        user_id=current_user.id
    )


# ==============================================================================
# Fiscal Years & Periods
# ==============================================================================

@router.get("/fiscal-years", response_model=List[FiscalYearResponse])
async def list_fiscal_years(
    current_user: CurrentUser = Depends(RequirePermission("financials:journal:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """List all fiscal years and their 12 monthly accounting periods."""
    return await FiscalPeriodService.list_fiscal_years(db, current_user.tenant_id)


@router.post("/fiscal-years", response_model=FiscalYearResponse, status_code=status.HTTP_201_CREATED)
async def create_fiscal_year(
    payload: FiscalYearCreate,
    current_user: CurrentUser = Depends(RequirePermission("financials:period:close")),
    db: AsyncSession = Depends(get_db_session)
):
    """Initialize a new fiscal year along with automated 12 monthly periods."""
    return await FiscalPeriodService.create_fiscal_year_with_12_periods(db, current_user.tenant_id, payload)


@router.post("/fiscal-periods/{period_id}/lock", response_model=FiscalPeriodResponse)
async def lock_fiscal_period(
    period_id: str,
    current_user: CurrentUser = Depends(RequirePermission("financials:period:close")),
    db: AsyncSession = Depends(get_db_session)
):
    """Lock a fiscal period to prevent further journal postings."""
    return await FiscalPeriodService.lock_period(db, current_user.tenant_id, period_id)


# ==============================================================================
# Fixed Assets & Depreciation
# ==============================================================================

@router.get("/fixed-assets", response_model=List[FixedAssetResponse])
async def list_fixed_assets(
    current_user: CurrentUser = Depends(RequirePermission("financials:assets:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """List fixed asset register and depreciation schedules."""
    return await FixedAssetService.list_assets(db, current_user.tenant_id)


@router.post("/fixed-assets", response_model=FixedAssetResponse, status_code=status.HTTP_201_CREATED)
async def register_fixed_asset(
    payload: FixedAssetCreate,
    current_user: CurrentUser = Depends(RequirePermission("financials:assets:manage")),
    db: AsyncSession = Depends(get_db_session)
):
    """Register fixed asset and compute monthly amortization schedule."""
    return await FixedAssetService.register_asset_with_schedule(db, current_user.tenant_id, payload)


# ==============================================================================
# Financial Reports
# ==============================================================================

@router.get("/reports/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    as_of_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("financials:reports:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate General Ledger Trial Balance report."""
    return await FinancialReportingService.generate_trial_balance(db, current_user.tenant_id, as_of_date)


@router.get("/reports/income-statement", response_model=IncomeStatementResponse)
async def get_income_statement(
    start_date: date = Query(...),
    end_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("financials:reports:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate Income Statement (P&L) for specified date range."""
    return await FinancialReportingService.generate_income_statement(db, current_user.tenant_id, start_date, end_date)


@router.get("/reports/balance-sheet", response_model=BalanceSheetResponse)
async def get_balance_sheet(
    as_of_date: date = Query(default_factory=date.today),
    current_user: CurrentUser = Depends(RequirePermission("financials:reports:view")),
    db: AsyncSession = Depends(get_db_session)
):
    """Generate Balance Sheet (Assets = Liabilities + Equity) as of specified date."""
    return await FinancialReportingService.generate_balance_sheet(db, current_user.tenant_id, as_of_date)
