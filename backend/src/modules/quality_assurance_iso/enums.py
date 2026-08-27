"""
Quality Assurance ISO Enums.
"""
import enum

class FMEARiskPriorityTier(str, enum.Enum):
    LOW_RPN_ACCEPTABLE = "LOW_RPN_ACCEPTABLE"      # RPN < 100
    MEDIUM_RPN_MONITOR = "MEDIUM_RPN_MONITOR"      # 100 <= RPN < 200
    HIGH_RPN_CRITICAL = "HIGH_RPN_CRITICAL"        # RPN >= 200

class PPAPLevel(str, enum.Enum):
    LEVEL_1 = "LEVEL_1" # Warrant only
    LEVEL_2 = "LEVEL_2" # Warrant with product samples
    LEVEL_3 = "LEVEL_3" # Full package with design records and control plan
    LEVEL_4 = "LEVEL_4" # Custom customer defined
    LEVEL_5 = "LEVEL_5" # On-site supplier review
