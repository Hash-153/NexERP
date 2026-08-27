"""
NexERP Procurement & Supply Chain Management (SCM) Database Models.
Handles Purchase Requisitions (PR), Requests for Quotation (RFQ), Purchase Orders (PO),
Goods Receipt Notes (GRN), and Vendor Scorecarding.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class PurchaseRequisition(Base):
    """
    Internal departmental spend request requiring management authorization.
    """
    __tablename__ = "scm_purchase_requisitions"

    requisition_number = Column(String(50), nullable=False, index=True, doc="e.g. 'PR-2026-0001'")
    department_id = Column(String(36), nullable=True, index=True)
    requested_by_id = Column(String(36), nullable=False, index=True)
    required_by_date = Column(Date, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, index=True, doc="DRAFT, PENDING_APPROVAL, APPROVED, REJECTED, ORDERED")
    estimated_total = Column(Numeric(18, 4), default=0.0, nullable=False)
    justification = Column(Text, nullable=True)
    
    approved_by_id = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    lines = relationship("PurchaseRequisitionLine", back_populates="requisition", cascade="all, delete-orphan")


class PurchaseRequisitionLine(Base):
    """
    Line item on purchase requisition.
    """
    __tablename__ = "scm_requisition_lines"

    requisition_id = Column(String(36), ForeignKey("scm_purchase_requisitions.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    estimated_unit_cost = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_estimated_cost = Column(Numeric(18, 4), default=0.0, nullable=False)

    requisition = relationship("PurchaseRequisition", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")


class RequestForQuotation(Base):
    """
    Request for Quotation (RFQ) bidding solicitation sent to prospective suppliers.
    """
    __tablename__ = "scm_rfqs"

    rfq_number = Column(String(50), nullable=False, index=True, doc="e.g. 'RFQ-2026-0001'")
    requisition_id = Column(String(36), ForeignKey("scm_purchase_requisitions.id"), nullable=True)
    issue_date = Column(Date, nullable=False)
    closing_date = Column(Date, nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False, doc="DRAFT, ISSUED, EVALUATED, CLOSED")
    notes = Column(Text, nullable=True)

    vendors = relationship("RFQVendorInvitation", back_populates="rfq", cascade="all, delete-orphan")


class RFQVendorInvitation(Base):
    """
    Vendor quote proposal submitted in response to an RFQ.
    """
    __tablename__ = "scm_rfq_vendor_invitations"

    rfq_id = Column(String(36), ForeignKey("scm_rfqs.id", ondelete="CASCADE"), nullable=False)
    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    
    status = Column(String(30), default="INVITED", nullable=False, doc="INVITED, QUOTED, DECLINED, AWARDED")
    quote_reference = Column(String(100), nullable=True)
    quote_amount = Column(Numeric(18, 4), nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    rfq = relationship("RequestForQuotation", back_populates="vendors")
    vendor = relationship("backend.src.modules.accounts_payable.models.Vendor")


class PurchaseOrder(Base):
    """
    Binding contract and Purchase Order (PO) issued to an approved supplier.
    """
    __tablename__ = "scm_purchase_orders"

    po_number = Column(String(50), nullable=False, index=True, doc="e.g. 'PO-2026-0001'")
    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    requisition_id = Column(String(36), ForeignKey("scm_purchase_requisitions.id"), nullable=True)
    
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=False)
    payment_terms_days = Column(Integer, default=30, nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, index=True, doc="DRAFT, PENDING_APPROVAL, APPROVED, ISSUED, PARTIALLY_RECEIVED, RECEIVED, CANCELLED")
    
    shipping_address = Column(Text, nullable=True)
    subtotal = Column(Numeric(18, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    approved_by_id = Column(String(36), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    vendor = relationship("backend.src.modules.accounts_payable.models.Vendor")
    lines = relationship("PurchaseOrderLine", back_populates="po", cascade="all, delete-orphan")
    receipts = relationship("GoodsReceiptNote", back_populates="po")

    __table_args__ = (
        Index("ix_scm_po_tenant_number", "tenant_id", "po_number", unique=True),
    )


class PurchaseOrderLine(Base):
    """
    Line item on Purchase Order tracking ordered, received, and billed quantities.
    """
    __tablename__ = "scm_po_lines"

    po_id = Column(String(36), ForeignKey("scm_purchase_orders.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity_ordered = Column(Numeric(18, 4), nullable=False)
    quantity_received = Column(Numeric(18, 4), default=0.0, nullable=False)
    quantity_billed = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    unit_price = Column(Numeric(18, 4), nullable=False)
    tax_rate_id = Column(String(36), ForeignKey("fin_tax_rates.id"), nullable=True)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    line_total = Column(Numeric(18, 4), nullable=False)

    po = relationship("PurchaseOrder", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")


class GoodsReceiptNote(Base):
    """
    Goods Receipt Note (GRN) logging received shipments at the receiving dock.
    """
    __tablename__ = "scm_goods_receipt_notes"

    grn_number = Column(String(50), nullable=False, index=True, doc="e.g. 'GRN-2026-0001'")
    po_id = Column(String(36), ForeignKey("scm_purchase_orders.id"), nullable=False)
    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    
    receipt_date = Column(Date, nullable=False)
    carrier_tracking_number = Column(String(100), nullable=True)
    status = Column(String(30), default="ACCEPTED", nullable=False, doc="RECEIVED, QC_HOLD, ACCEPTED, REJECTED")
    
    stock_movement_id = Column(String(36), ForeignKey("inv_stock_movements.id"), nullable=True)
    notes = Column(Text, nullable=True)

    po = relationship("PurchaseOrder", back_populates="receipts")
    vendor = relationship("backend.src.modules.accounts_payable.models.Vendor")
    warehouse = relationship("backend.src.modules.inventory.models.Warehouse")
    lines = relationship("GoodsReceiptLine", back_populates="grn", cascade="all, delete-orphan")


class GoodsReceiptLine(Base):
    """
    Individual item inspection and receipt quantity row on GRN.
    """
    __tablename__ = "scm_grn_lines"

    grn_id = Column(String(36), ForeignKey("scm_goods_receipt_notes.id", ondelete="CASCADE"), nullable=False)
    po_line_id = Column(String(36), ForeignKey("scm_po_lines.id"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    
    quantity_received = Column(Numeric(18, 4), nullable=False)
    quantity_accepted = Column(Numeric(18, 4), nullable=False)
    quantity_rejected = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id"), nullable=False)
    lot_number = Column(String(100), nullable=True)

    grn = relationship("GoodsReceiptNote", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")
    location = relationship("backend.src.modules.inventory.models.WarehouseLocation")


class VendorEvaluation(Base):
    """
    Vendor Scorecard ranking supplier on Quality, Delivery, and Pricing competitiveness.
    """
    __tablename__ = "scm_vendor_evaluations"

    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    evaluation_date = Column(Date, nullable=False)
    
    quality_score = Column(Numeric(5, 2), default=100.0, nullable=False, doc="0-100 score based on QC rejection rates")
    on_time_delivery_score = Column(Numeric(5, 2), default=100.0, nullable=False, doc="0-100 score based on delivery schedule adherence")
    pricing_score = Column(Numeric(5, 2), default=100.0, nullable=False, doc="0-100 score on price competitiveness")
    overall_rating = Column(Numeric(5, 2), nullable=False)
    
    evaluator_id = Column(String(36), nullable=True)
    remarks = Column(Text, nullable=True)

    vendor = relationship("backend.src.modules.accounts_payable.models.Vendor")
