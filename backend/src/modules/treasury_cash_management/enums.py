"""
Treasury & Cash Management Enums.
"""
import enum

class BankStatementFormat(str, enum.Enum):
    MT940 = "MT940"
    BAI2 = "BAI2"
    CAMT053 = "CAMT053"
    CSV_CUSTOM = "CSV_CUSTOM"

class TreasuryTransactionType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    SWEEP_IN = "SWEEP_IN"
    SWEEP_OUT = "SWEEP_OUT"
    FX_SPOT = "FX_SPOT"
    FX_FORWARD = "FX_FORWARD"
    INTEREST_INCOME = "INTEREST_INCOME"
    BANK_FEE = "BANK_FEE"

class HedgingInstrumentType(str, enum.Enum):
    FORWARD_CONTRACT = "FORWARD_CONTRACT"
    VANILLA_OPTION = "VANILLA_OPTION"
    CURRENCY_SWAP = "CURRENCY_SWAP"
    INTEREST_RATE_SWAP = "INTEREST_RATE_SWAP"

class SettlementStatus(str, enum.Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    TRANSMITTED = "TRANSMITTED"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"

class LiquidityTier(str, enum.Enum):
    TIER_1_OPERATIONAL = "TIER_1_OPERATIONAL"      # 0-30 days liquid
    TIER_2_SHORT_TERM = "TIER_2_SHORT_TERM"        # 30-90 days money market
    TIER_3_STRATEGIC = "TIER_3_STRATEGIC"          # 90+ days reserve capital
