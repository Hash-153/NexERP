"""
Treasury & Cash Management REST API Router.
"""
from typing import List, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.src.core.database import get_db_session
from backend.src.core.dependencies import get_current_user, CurrentUser
from .models import TreasuryBankAccount, FXHedgingContract, CashPositionForecast
from .schemas import (
    TreasuryBankAccountCreate, TreasuryBankAccountResponse,
    StatementImportRequest, FXHedgingContractCreate, FXHedgingContractResponse,
    CashForecastRequest
)
from .services import (
    BankStatementParserService, CashPositioningService,
    FXHedgingService, LiquidityForecastingService, IntercompanySweepService
)

router = APIRouter(prefix="/treasury", tags=["Treasury & Cash Management"])

@router.get("/accounts", response_model=List[TreasuryBankAccountResponse])
async def list_treasury_accounts(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    stmt = select(TreasuryBankAccount).where(
        TreasuryBankAccount.tenant_id == user.tenant_id,
        TreasuryBankAccount.is_deleted == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/accounts", response_model=TreasuryBankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_treasury_account(
    payload: TreasuryBankAccountCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    account = TreasuryBankAccount(
        tenant_id=user.tenant_id,
        account_number=payload.account_number,
        iban=payload.iban,
        swift_bic=payload.swift_bic,
        bank_name=payload.bank_name,
        branch_name=payload.branch_name,
        currency=payload.currency,
        account_type=payload.account_type,
        gl_account_id=payload.gl_account_id,
        current_ledger_balance=payload.initial_balance,
        available_cleared_balance=payload.initial_balance,
        overdraft_limit=payload.overdraft_limit,
        target_balance=payload.target_balance,
        is_sweep_target=payload.is_sweep_target,
        is_sweep_source=payload.is_sweep_source
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account

@router.get("/cash-position")
async def get_cash_position(
    currency: str = Query("USD", max_length=3),
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await CashPositioningService.get_intraday_cash_position(
        session=db,
        tenant_id=user.tenant_id,
        base_currency=currency
    )

@router.post("/statements/import")
async def import_bank_statement(
    payload: StatementImportRequest,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    statement = await BankStatementParserService.import_parsed_statement(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
    return {"status": "SUCCESS", "statement_id": statement.id, "identifier": statement.statement_identifier}

@router.post("/fx-contracts", response_model=FXHedgingContractResponse)
async def create_fx_hedge(
    payload: FXHedgingContractCreate,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await FXHedgingService.create_forward_contract(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/forecasts/generate")
async def generate_cash_forecast(
    payload: CashForecastRequest,
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    return await LiquidityForecastingService.generate_rolling_forecast(
        session=db,
        payload=payload,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )

@router.post("/sweeps/execute")
async def execute_intercompany_sweeps(
    db: AsyncSession = Depends(get_db_session),
    user: CurrentUser = Depends(get_current_user)
):
    results = await IntercompanySweepService.execute_zero_balance_sweeps(
        session=db,
        tenant_id=user.tenant_id,
        actor_id=user.id
    )
    return {"status": "EXECUTED", "sweeps": results}
