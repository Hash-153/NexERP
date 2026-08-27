"""
NexERP Sales & CRM Module Services.
"""

from .lead_service import LeadService
from .quotation_service import QuotationService
from .sales_order_service import SalesOrderService
from .fulfillment_service import FulfillmentService
from .pricing_engine_service import PricingEngineService
from .commission_engine_service import CommissionEngineService

SalesCommissionService = CommissionEngineService
from .rma_service import RMAService
from .cpq_rules_engine_service import CPQRulesEngineService
from .customer_rebates_service import CustomerRebatesService
from .field_service_dispatch_service import FieldServiceDispatchService

DeliveryService = FulfillmentService
TieredPricingService = PricingEngineService
CommercialPricingService = PricingEngineService
CRMPipelineService = LeadService

__all__ = [
    "LeadService",
    "CRMPipelineService",
    "QuotationService",
    "SalesOrderService",
    "FulfillmentService",
    "DeliveryService",
    "PricingEngineService",
    "TieredPricingService",
    "CommercialPricingService",
    "SalesCommissionService",
    "RMAService",
    "CPQRulesEngineService",
    "CustomerRebatesService",
    "FieldServiceDispatchService",
]
