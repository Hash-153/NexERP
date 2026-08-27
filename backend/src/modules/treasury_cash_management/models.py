"""
Treasury & Cash Management Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class TreasuryBankAccount(Base):
    """Corporate Bank Account registered for treasury operations."""
    __tablename__ = "treasury_bank_accounts"

    account_number = Column(String(64), nullable=False, index=True)
    iban = Column(String(34), nullable=True, index=True)
    swift_bic = Column(String(11), nullable=False)
    bank_name = Column(String(150), nullable=False)
    branch_name = Column(String(150), nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    account_type = Column(String(50), default="CHECKING", nullable=False)  # CHECKING, SAVINGS, SWEEP, ESCROW
    gl_account_id = Column(String(36), nullable=True, doc="Linked GL account in chart of accounts")
    
    current_ledger_balance = Column(Numeric(18, 4), default=0.0, nullable=False)
    available_cleared_balance = Column(Numeric(18, 4), default=0.0, nullable=False)
    overdraft_limit = Column(Numeric(18, 4), default=0.0, nullable=False)
    target_balance = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    is_sweep_target = Column(Boolean, default=False, nullable=False)
    is_sweep_source = Column(Boolean, default=False, nullable=False)
    sweep_pool_id = Column(String(36), nullable=True)
    
    statements = relationship("TreasuryBankStatement", back_populates="bank_account", cascade="all, delete-orphan")
    transactions = relationship("TreasuryTransaction", back_populates="bank_account")


class TreasuryBankStatement(Base):
    """Electronic Bank Statement parsed into NexERP."""
    __tablename__ = "treasury_bank_statements"

    bank_account_id = Column(String(36), ForeignKey("treasury_bank_accounts.id", ondelete="CASCADE"), nullable=False)
    statement_identifier = Column(String(100), nullable=False, index=True)
    statement_format = Column(String(20), default="CAMT053", nullable=False)
    statement_date = Column(Date, nullable=False)
    opening_balance = Column(Numeric(18, 4), nullable=False)
    closing_balance = Column(Numeric(18, 4), nullable=False)
    total_debits = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_credits = Column(Numeric(18, 4), default=0.0, nullable=False)
    is_reconciled = Column(Boolean, default=False, nullable=False)
    reconciled_at = Column(DateTime(timezone=True), nullable=True)
    raw_payload = Column(Text, nullable=True)

    bank_account = relationship("TreasuryBankAccount", back_populates="statements")
    lines = relationship("TreasuryBankStatementLine", back_populates="statement", cascade="all, delete-orphan")


class TreasuryBankStatementLine(Base):
    """Granular line item from an electronic bank statement."""
    __tablename__ = "treasury_bank_statement_lines"

    statement_id = Column(String(36), ForeignKey("treasury_bank_statements.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    booking_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    transaction_code = Column(String(30), nullable=True)
    bank_reference = Column(String(100), nullable=True, index=True)
    remittance_info = Column(Text, nullable=True)
    counterparty_name = Column(String(255), nullable=True)
    counterparty_iban = Column(String(34), nullable=True)
    matched_transaction_id = Column(String(36), nullable=True)
    is_matched = Column(Boolean, default=False, nullable=False)

    statement = relationship("TreasuryBankStatement", back_populates="lines")


class TreasuryTransaction(Base):
    """Treasury operational transaction recorded in the ledger."""
    __tablename__ = "treasury_transactions"

    bank_account_id = Column(String(36), ForeignKey("treasury_bank_accounts.id"), nullable=False)
    transaction_reference = Column(String(64), nullable=False, unique=True, index=True)
    transaction_type = Column(String(40), nullable=False)
    booking_date = Column(Date, nullable=False)
    value_date = Column(Date, nullable=False)
    amount = Column(Numeric(18, 4), nullable=False)
    currency = Column(String(3), nullable=False)
    base_currency_amount = Column(Numeric(18, 4), nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    counterparty_entity = Column(String(255), nullable=True)
    counterparty_account = Column(String(64), nullable=True)
    status = Column(String(30), default="CONFIRMED", nullable=False)
    notes = Column(Text, nullable=True)
    journal_entry_id = Column(String(36), nullable=True)

    bank_account = relationship("TreasuryBankAccount", back_populates="transactions")


class FXHedgingContract(Base):
    """Foreign Exchange Hedging Forward/Option Contract."""
    __tablename__ = "treasury_fx_hedging_contracts"

    contract_number = Column(String(64), nullable=False, unique=True, index=True)
    instrument_type = Column(String(40), default="FORWARD_CONTRACT", nullable=False)
    counterparty_bank = Column(String(150), nullable=False)
    deal_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=False)
    
    buy_currency = Column(String(3), nullable=False)
    buy_amount = Column(Numeric(18, 4), nullable=False)
    sell_currency = Column(String(3), nullable=False)
    sell_amount = Column(Numeric(18, 4), nullable=False)
    contracted_forward_rate = Column(Numeric(18, 6), nullable=False)
    spot_rate_at_inception = Column(Numeric(18, 6), nullable=False)
    
    current_market_rate = Column(Numeric(18, 6), nullable=True)
    mark_to_market_value = Column(Numeric(18, 4), default=0.0, nullable=False)
    hedge_designation = Column(String(50), default="CASH_FLOW_HEDGE", nullable=False)  # CASH_FLOW_HEDGE, FAIR_VALUE_HEDGE
    hedge_effectiveness_ratio = Column(Numeric(8, 4), default=1.0, nullable=False)
    is_settled = Column(Boolean, default=False, nullable=False)
    settlement_date = Column(Date, nullable=True)
    realized_gain_loss = Column(Numeric(18, 4), default=0.0, nullable=False)


class CashPositionForecast(Base):
    """Rolling multi-period cash forecast aggregation."""
    __tablename__ = "treasury_cash_forecasts"

    forecast_code = Column(String(64), nullable=False, index=True)
    as_of_date = Column(Date, nullable=False)
    horizon_days = Column(Integer, default=90, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    opening_liquid_cash = Column(Numeric(18, 4), nullable=False)
    expected_ar_inflows = Column(Numeric(18, 4), default=0.0, nullable=False)
    expected_ap_outflows = Column(Numeric(18, 4), default=0.0, nullable=False)
    expected_payroll_outflows = Column(Numeric(18, 4), default=0.0, nullable=False)
    expected_capex_outflows = Column(Numeric(18, 4), default=0.0, nullable=False)
    net_projected_position = Column(Numeric(18, 4), nullable=False)
    minimum_buffer_threshold = Column(Numeric(18, 4), default=0.0, nullable=False)
    liquidity_surplus_deficit = Column(Numeric(18, 4), nullable=False)
    forecast_breakdown_json = Column(JSON, nullable=True)
