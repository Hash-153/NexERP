"""
NexERP Quality Control Module Services.
"""

from .quality_plan_service import QualityPlanService
from .inspection_service import InspectionService
from .ncr_capa_service import NCRService
from .spc_control_chart_service import SPCControlChartService
from .aql_sampling_service import AQLSamplingService
from .eight_d_corrective_action_service import EightDCorrectiveActionService
from .fmea_risk_service import FMEARiskService
from .scar_service import SCARManagementService

NonConformanceService = NCRService

__all__ = [
    "QualityPlanService",
    "InspectionService",
    "NCRService",
    "NonConformanceService",
    "SPCControlChartService",
    "AQLSamplingService",
    "EightDCorrectiveActionService",
    "FMEARiskService",
    "SCARManagementService",
]
