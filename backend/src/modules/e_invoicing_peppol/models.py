"""
Global E-Invoicing & PEPPOL Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class EInvoiceTransmissionRecord(Base):
    """Universal E-Invoice transmission envelope tracking electronic tax invoices."""
    __tablename__ = "einv_transmissions"

    invoice_id = Column(String(36), nullable=False, index=True)
    invoice_number = Column(String(64), nullable=False, index=True)
    standard = Column(String(40), default="PEPPOL_BIS_BILLING_3", nullable=False)
    transmission_status = Column(String(40), default="GENERATED", nullable=False)
    
    buyer_endpoint_id = Column(String(100), nullable=False)  # e.g. 0088:7300010000001 (EAN)
    seller_endpoint_id = Column(String(100), nullable=False)
    tax_authority_uuid = Column(String(100), nullable=True, index=True)
    qr_code_payload = Column(Text, nullable=True)
    
    xml_payload = Column(Text, nullable=False)
    validation_report_json = Column(JSON, nullable=True)
    transmitted_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
