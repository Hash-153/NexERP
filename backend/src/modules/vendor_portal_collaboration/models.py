"""
Vendor Collaboration Portal Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class AdvanceShippingNoticeASN(Base):
    """Vendor-generated Advance Shipping Notice (ASN) with SSCC-18 pallet barcode."""
    __tablename__ = "vp_asn_shipments"

    vendor_id = Column(String(36), nullable=False, index=True)
    purchase_order_id = Column(String(36), nullable=False, index=True)
    asn_number = Column(String(64), nullable=False, unique=True, index=True)
    sscc_barcode = Column(String(30), nullable=False, index=True)
    status = Column(String(30), default="TRANSMITTED", nullable=False)
    
    shipped_date = Column(DateTime(timezone=True), nullable=False)
    estimated_dock_arrival = Column(DateTime(timezone=True), nullable=False)
    carrier_tracking_number = Column(String(100), nullable=True)
    
    total_cartons = Column(Integer, default=1, nullable=False)
    total_shipped_qty = Column(Numeric(14, 4), nullable=False)
    total_received_qty = Column(Numeric(14, 4), default=0.0, nullable=False)
    is_discrepancy = Column(Boolean, default=False, nullable=False)


class VendorPortalInvoiceSubmission(Base):
    """Digital supplier invoice submitted for 3-way matching."""
    __tablename__ = "vp_invoice_submissions"

    vendor_id = Column(String(36), nullable=False, index=True)
    purchase_order_id = Column(String(36), nullable=False, index=True)
    invoice_number = Column(String(64), nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    subtotal_amount = Column(Numeric(14, 4), nullable=False)
    tax_amount = Column(Numeric(14, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(14, 4), nullable=False)
    
    is_matched_3way = Column(Boolean, default=False, nullable=False)
    match_status = Column(String(30), default="PENDING_MATCH", nullable=False)
    discrepancy_reason = Column(String(255), nullable=True)
