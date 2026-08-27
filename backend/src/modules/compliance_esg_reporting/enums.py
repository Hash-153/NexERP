"""
ESG & Carbon Emissions Enums.
"""
import enum

class EmissionScope(str, enum.Enum):
    SCOPE_1_DIRECT = "SCOPE_1_DIRECT"                # Stationary/Mobile fuel combustion
    SCOPE_2_MARKET_BASED = "SCOPE_2_MARKET_BASED"    # Purchased grid electricity
    SCOPE_2_LOCATION_BASED = "SCOPE_2_LOCATION_BASED"# Regional grid average
    SCOPE_3_VALUE_CHAIN = "SCOPE_3_VALUE_CHAIN"      # Purchased goods, transport, business travel

class FuelCombustionType(str, enum.Enum):
    NATURAL_GAS = "NATURAL_GAS"
    DIESEL_STATIONARY = "DIESEL_STATIONARY"
    FLEET_GASOLINE = "FLEET_GASOLINE"
    LPG_PROPANE = "LPG_PROPANE"

class ESGReportingStandard(str, enum.Enum):
    GHG_PROTOCOL = "GHG_PROTOCOL"
    CSRD_ESRS = "CSRD_ESRS"
    SEC_CLIMATE_RULE = "SEC_CLIMATE_RULE"
    GRI_STANDARDS = "GRI_STANDARDS"
