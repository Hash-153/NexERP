"""
NexERP Accounts Receivable (AR) Database Models.
Handles Customer Accounts, Sales Invoices, Payment Receipts & Allocations, Credit Memos, and Dunning Notices.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Customer(Base):
    """
    Customer Master account with credit limits, terms, and address profiles.
    """
    __tablename__ = "ar_customers"

    customer_number = Column(String(50), nullable=False, index=True, doc="e.g. 'CUST-00101'")
    name = Column(String(150), nullable=False)
    tax_identifier = Column(String(50), nullable=True)
    customer_group = Column(String(50), default="Commercial", nullable=False)
    
    payment_terms_days = Column(Integer, default=30, nullable=False)
    credit_limit = Column(Numeric(18, 4), default=50000.0, nullable=False)
    credit_hold = Column(Boolean, default=False, nullable=False, doc="Blocks new sales orders if credit limit breached")
    current_balance = Column(Numeric(18, 4), default=0.0, nullable=False, doc="Total uncollected receivables")
    
    currency = Column(String(3), default="USD", nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    billing_address = Column(Text, nullable=True)
    shipping_address = Column(Text, nullable=True)
    
    ar_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="GL Accounts Receivable Asset account")
    revenue_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=True, doc="Default GL Sales Revenue account")

    invoices = relationship("SalesInvoice", back_populates="customer")
    receipts = relationship("PaymentReceipt", back_populates="customer")

    __table_args__ = (
        Index("ix_ar_customer_tenant_code", "tenant_id", "customer_number", unique=True),
    )


class SalesInvoice(Base):
    """
    Sales Invoice issued to a customer for products shipped or services rendered.
    """
    __tablename__ = "ar_sales_invoices"

    invoice_number = Column(String(50), nullable=False, index=True, doc="e.g. 'INV-2026-0001'")
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    status = Column(String(30), default="DRAFT", nullable=False, index=True, doc="DRAFT, POSTED, PAID, PARTIALLY_PAID, CANCELLED")
    
    sales_order_id = Column(String(36), nullable=True, index=True)
    fulfillment_delivery_id = Column(String(36), nullable=True, index=True)
    
    subtotal = Column(Numeric(18, 4), default=0.0, nullable=False)
    discount_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    paid_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    balance_due = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    dunning_level = Column(Integer, default=0, nullable=False, doc="0=Current, 1=Reminder, 2=Warning, 3=Demand")
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="invoices")
    lines = relationship("SalesInvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    allocations = relationship("ReceiptAllocation", back_populates="invoice")

    __table_args__ = (
        Index("ix_ar_invoice_tenant_number", "tenant_id", "invoice_number", unique=True),
    )


class SalesInvoiceLine(Base):
    """
    Line item on customer sales invoice detailing products, quantities, discounts, and taxes.
    """
    __tablename__ = "ar_sales_invoice_lines"

    invoice_id = Column(String(36), ForeignKey("ar_sales_invoices.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), nullable=True, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(7, 4), default=0.0, nullable=False)
    
    tax_rate_id = Column(String(36), ForeignKey("fin_tax_rates.id"), nullable=True)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    line_total = Column(Numeric(18, 4), nullable=False)
    
    revenue_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    cost_center_id = Column(String(36), nullable=True)
    project_id = Column(String(36), nullable=True)

    invoice = relationship("SalesInvoice", back_populates="lines")


class PaymentReceipt(Base):
    """
    Customer payment receipt record for cash, wire, or credit card collection.
    """
    __tablename__ = "ar_payment_receipts"

    receipt_number = Column(String(50), nullable=False, index=True, doc="e.g. 'RCT-2026-0001'")
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    
    receipt_date = Column(Date, nullable=False)
    bank_account_id = Column(String(36), ForeignKey("fin_accounts.id"), nullable=False)
    payment_method = Column(String(50), default="WIRE_TRANSFER", nullable=False)
    
    total_amount = Column(Numeric(18, 4), nullable=False)
    unallocated_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="POSTED", nullable=False)
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)
    notes = Column(Text, nullable=True)

    customer = relationship("Customer", back_populates="receipts")
    allocations = relationship("ReceiptAllocation", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptAllocation(Base):
    """
    Settlement mapping linking a Payment Receipt to an outstanding Sales Invoice.
    """
    __tablename__ = "ar_receipt_allocations"

    receipt_id = Column(String(36), ForeignKey("ar_payment_receipts.id", ondelete="CASCADE"), nullable=False)
    invoice_id = Column(String(36), ForeignKey("ar_sales_invoices.id"), nullable=False)
    allocated_amount = Column(Numeric(18, 4), nullable=False)
    early_discount_taken = Column(Numeric(18, 4), default=0.0, nullable=False)

    receipt = relationship("PaymentReceipt", back_populates="allocations")
    invoice = relationship("SalesInvoice", back_populates="allocations")


class CreditMemo(Base):
    """
    Credit Note / Memo issued to customer for sales returns or billing adjustments.
    """
    __tablename__ = "ar_credit_memos"

    credit_memo_number = Column(String(50), nullable=False, index=True)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    invoice_id = Column(String(36), ForeignKey("ar_sales_invoices.id"), nullable=True)
    
    issue_date = Column(Date, nullable=False)
    reason = Column(String(255), nullable=False)
    total_amount = Column(Numeric(18, 4), nullable=False)
    balance_remaining = Column(Numeric(18, 4), nullable=False)
    status = Column(String(30), default="POSTED", nullable=False)
    
    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=True)


class DunningNotice(Base):
    """
    Dunning collection notice issued to overdue customer accounts.
    """
    __tablename__ = "ar_dunning_notices"

    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    dunning_level = Column(Integer, nullable=False)
    notice_date = Column(Date, nullable=False)
    overdue_balance = Column(Numeric(18, 4), nullable=False)
    interest_charged = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="ISSUED", nullable=False)
