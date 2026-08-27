"""
NexERP Procurement & SCM Module Services.
"""

from .requisition_service import RequisitionService
from .purchase_order_service import PurchaseOrderService
from .goods_receipt_service import GoodsReceiptService
from .rfq_auction_service import RFQAuctionService
from .landed_cost_service import LandedCostService
from .supplier_evaluation_service import SupplierEvaluationService
from .carrier_routing_service import CarrierRatingService
from .customs_harmonized_tariff_service import CustomsTariffService
from .consignment_inventory_service import ConsignmentInventoryService
from .freight_audit_service import FreightAuditService

PurchaseRequisitionService = RequisitionService
VendorEvaluationService = SupplierEvaluationService

__all__ = [
    "RequisitionService",
    "PurchaseRequisitionService",
    "PurchaseOrderService",
    "GoodsReceiptService",
    "RFQAuctionService",
    "LandedCostService",
    "SupplierEvaluationService",
    "VendorEvaluationService",
    "CarrierRatingService",
    "CustomsTariffService",
    "ConsignmentInventoryService",
    "FreightAuditService",
]
