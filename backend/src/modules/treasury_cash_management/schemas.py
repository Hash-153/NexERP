"""
Treasury & Cash Management Pydantic Schemas.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class TreasuryBankAccountBase(BaseModel):
    account_number: str = Field(..., max_length=64)
    iban: Optional[str] = Field(None, max_length=34)
    swift_bic: str = Field(..., max_length=11)
    bank_name: str = Field(..., max_length=150)
    branch_name: Optional[str] = None
    currency: str = Field(default="USD", max_length=3)
    account_type: str = Field(default="CHECKING")
    gl_account_id: Optional[str] = None
    overdraft_limit: Decimal = Decimal("0.0")
    target_balance: Decimal = Decimal("0.0")
    is_sweep_target: bool = False
    is_sweep_source: bool = False

class TreasuryBankAccountCreate(TreasuryBankAccountBase):
    initial_balance: Decimal = Decimal("0.0")

class TreasuryBankAccountResponse(TreasuryBankAccountBase):
    id: str
    tenant_id: str
    current_ledger_balance: Decimal
    available_cleared_balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class StatementLineItem(BaseModel):
    line_number: int
    booking_date: date
    value_date: date
    amount: Decimal
    currency: str
    transaction_code: Optional[str] = None
    bank_reference: Optional[str] = None
    remittance_info: Optional[str] = None
    counterparty_name: Optional[str] = None
    counterparty_iban: Optional[str] = None

class StatementImportRequest(BaseModel):
    bank_account_id: str
    statement_identifier: str
    statement_format: str = "CAMT053"
    statement_date: date
    opening_balance: Decimal
    closing_balance: Decimal
    raw_payload: Optional[str] = None
    lines: List[StatementLineItem]

class FXHedgingContractCreate(BaseModel):
    contract_number: str
    instrument_type: str = "FORWARD_CONTRACT"
    counterparty_bank: str
    deal_date: date
    maturity_date: date
    buy_currency: str
    buy_amount: Decimal
    sell_currency: str
    sell_amount: Decimal
    contracted_forward_rate: Decimal
    spot_rate_at_inception: Decimal
    hedge_designation: str = "CASH_FLOW_HEDGE"

class FXHedgingContractResponse(FXHedgingContractCreate):
    id: str
    tenant_id: str
    current_market_rate: Optional[Decimal] = None
    mark_to_market_value: Decimal
    hedge_effectiveness_ratio: Decimal
    is_settled: bool
    settlement_date: Optional[date] = None
    realized_gain_loss: Decimal

    model_config = ConfigDict(from_attributes=True)

class CashForecastRequest(BaseModel):
    horizon_days: int = 90
    currency: str = "USD"
    minimum_buffer: Decimal = Decimal("500000.00")
