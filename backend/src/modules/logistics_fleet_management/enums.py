"""
Logistics & Fleet Management Enums.
"""
import enum

class TransportMode(str, enum.Enum):
    ROAD_LTL = "ROAD_LTL"
    ROAD_FTL = "ROAD_FTL"
    OCEAN_FCL = "OCEAN_FCL"
    OCEAN_LCL = "OCEAN_LCL"
    AIR_EXPRESS = "AIR_EXPRESS"
    RAIL_INTERMODAL = "RAIL_INTERMODAL"

class FreightClass(str, enum.Enum):
    CLASS_50 = "50"
    CLASS_70 = "70"
    CLASS_100 = "100"
    CLASS_150 = "150"
    CLASS_250 = "250"
    CLASS_500 = "500"

class ShipmentDispatchStatus(str, enum.Enum):
    BOOKED = "BOOKED"
    DISPATCHED = "DISPATCHED"
    IN_TRANSIT = "IN_TRANSIT"
    CUSTOMS_HOLD = "CUSTOMS_HOLD"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    EXCEPTION_DELAY = "EXCEPTION_DELAY"
