"""
NexERP Accounts Payable (AP) Database Models.
Handles Vendor Profiles, Vendor Invoices/Bills, 3-Way Matching Logs, Batch Payment Runs, and Debit Notes.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Vendor(Base):
    """
    Vendor / Supplier master record.
    """
    __tablename__ = "ap_vendors"

    code = Column(String(50), nullable=False, index=True, doc="Unique supplier code, e.g. 'VEND-00101'")
    name = Column(String(150), nullable=False)
    tax_identifier = Column(String(50), nullable=True, doc="Tax ID / EIN / VAT number")
    payment_terms_days = Column(Integer, default=30, nullable=False, doc="Net payment term in days")
    credit_limit = Column(Numeric(18, 4), default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    bank_account_details = Column(Text, nullable=True)
    
    ap_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="Default GL Accounts Payable liability account")
    expense_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="Default GL Expense account")
    
    is_1099_eligible = Column(Boolean, default=False, nullable=False)

    bills = relationship("VendorBill", back_populates="vendor")
    debit_notes = relationship("DebitNote", back_populates="vendor")

    __table_args__ = (
        Index("ix_ap_vendor_tenant_code", "tenant_id", "code", unique=True),
    )


class VendorBill(Base):
    """
    Vendor Bill / Invoice received from a supplier for goods or services.
    """
    __tablename__ = "ap_vendor_bills"

    bill_number = Column(String(100), nullable=False, index=True, doc="Vendor's invoice number")
    system_reference = Column(String(50), nullable=False, index=True, doc="Internal tracking voucher, e.g. 'BILL-2026-0001'")
    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    
    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, index=True, doc="DRAFT, SUBMITTED, APPROVED, PAID, CANCELLED")
    
    purchase_order_id = Column(String(36), nullable=True, index=True)
    goods_receipt_id = Column(String(36), nullable=True, index=True)
    
    subtotal = Column(Numeric(18, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    paid_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    balance_due = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)
    notes = Column(Text, nullable=True)

    vendor = relationship("Vendor", back_populates="bills")
    lines = relationship("VendorBillLine", back_populates="bill", cascade="all, delete-orphan")
    match_logs = relationship("ThreeWayMatchLog", back_populates="bill", cascade="all, delete-orphan")


class VendorBillLine(Base):
    """
    Line item on a vendor bill detailing item, quantity, unit price, and expense distribution.
    """
    __tablename__ = "ap_vendor_bill_lines"

    bill_id = Column(String(36), ForeignKey("ap_vendor_bills.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), nullable=True, index=True, doc="Optional inventory item linkage")
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False)
    
    tax_rate_id = Column(String(36), ForeignKey("fin_tax_rates.id"), nullable=True)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    line_total = Column(Numeric(18, 4), nullable=False)
    
    expense_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    cost_center_id = Column(String(36), nullable=True)
    project_id = Column(String(36), nullable=True)

    bill = relationship("VendorBill", back_populates="lines")


class ThreeWayMatchLog(Base):
    """
    Forensic record of 3-Way Matching audit between PO, Goods Receipt Note (GRN), and Vendor Bill.
    """
    __tablename__ = "ap_three_way_match_logs"

    bill_id = Column(String(36), ForeignKey("ap_vendor_bills.id", ondelete="CASCADE"), nullable=False)
    purchase_order_id = Column(String(36), nullable=True)
    goods_receipt_id = Column(String(36), nullable=True)
    
    is_matched = Column(Boolean, default=False, nullable=False)
    price_variance_percent = Column(Numeric(7, 4), default=0.0, nullable=False)
    quantity_variance_percent = Column(Numeric(7, 4), default=0.0, nullable=False)
    tolerance_exceeded = Column(Boolean, default=False, nullable=False)
    
    matched_at = Column(DateTime(timezone=True), nullable=False)
    details = Column(JSON, nullable=True)

    bill = relationship("VendorBill", back_populates="match_logs")


class PaymentRun(Base):
    """
    Batch payment execution grouping multiple vendor bills for check or wire disbursement.
    """
    __tablename__ = "ap_payment_runs"

    run_number = Column(String(50), nullable=False, index=True)
    run_date = Column(Date, nullable=False)
    bank_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    payment_method = Column(String(50), default="WIRE_TRANSFER", nullable=False)
    
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False, doc="DRAFT, POSTED, CANCELLED")
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)
    notes = Column(Text, nullable=True)

    items = relationship("PaymentRunItem", back_populates="payment_run", cascade="all, delete-orphan")


class PaymentRunItem(Base):
    """
    Individual bill allocation within a batch payment run.
    """
    __tablename__ = "ap_payment_run_items"

    payment_run_id = Column(String(36), ForeignKey("ap_payment_runs.id", ondelete="CASCADE"), nullable=False)
    bill_id = Column(String(36), ForeignKey("ap_vendor_bills.id"), nullable=False)
    payment_amount = Column(Numeric(18, 4), nullable=False)
    early_discount_captured = Column(Numeric(18, 4), default=0.0, nullable=False)

    payment_run = relationship("PaymentRun", back_populates="items")


class DebitNote(Base):
    """
    Debit adjustment or vendor credit note issued for returned goods or billing adjustments.
    """
    __tablename__ = "ap_debit_notes"

    debit_note_number = Column(String(50), nullable=False, index=True)
    vendor_id = Column(String(36), ForeignKey("ap_vendors.id"), nullable=False)
    bill_id = Column(String(36), ForeignKey("ap_vendor_bills.id"), nullable=True)
    
    issue_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=False)
    total_amount = Column(Numeric(18, 4), nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False)
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)

    vendor = relationship("Vendor", back_populates="debit_notes")
