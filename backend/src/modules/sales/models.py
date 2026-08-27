"""
NexERP Sales Order Processing, Customer Pricing & Fulfillment Database Models.
Handles CRM Leads, Tiered Price Books, Quotations, Sales Orders (SO), Pick-Pack-Ship Deliveries, and RMAs.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Lead(Base):
    """
    CRM prospective sales opportunity.
    """
    __tablename__ = "sales_leads"

    lead_number = Column(String(50), nullable=False, index=True)
    contact_name = Column(String(150), nullable=False)
    company_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    stage = Column(String(30), default="NEW", nullable=False, index=True, doc="NEW, CONTACTED, QUALIFIED, PROPOSAL, WON, LOST")
    estimated_value = Column(Numeric(18, 4), default=0.0, nullable=False)
    win_probability_percent = Column(Integer, default=20, nullable=False)
    
    assigned_sales_rep_id = Column(String(36), nullable=True, index=True)
    source = Column(String(100), default="Website", nullable=False)
    notes = Column(Text, nullable=True)


class CustomerPriceBook(Base):
    """
    Tiered customer contract pricing schedule.
    """
    __tablename__ = "sales_price_books"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)

    items = relationship("PriceBookItem", back_populates="price_book", cascade="all, delete-orphan")


class PriceBookItem(Base):
    """
    Specific item price point or volume tiered discount.
    """
    __tablename__ = "sales_price_book_items"

    price_book_id = Column(String(36), ForeignKey("sales_price_books.id", ondelete="CASCADE"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    min_quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    fixed_price = Column(Numeric(18, 4), nullable=True)
    discount_percent = Column(Numeric(7, 4), default=0.0, nullable=False)

    price_book = relationship("CustomerPriceBook", back_populates="items")
    item = relationship("backend.src.modules.inventory.models.Item")


class SalesQuotation(Base):
    """
    Sales quotation / commercial proposal submitted to client.
    """
    __tablename__ = "sales_quotations"

    quote_number = Column(String(50), nullable=False, index=True, doc="e.g. 'QT-2026-0001'")
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    lead_id = Column(String(36), ForeignKey("sales_leads.id"), nullable=True)
    
    quote_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(String(30), default="DRAFT", nullable=False, doc="DRAFT, SENT, ACCEPTED, REJECTED, EXPIRED")
    
    currency = Column(String(3), default="USD", nullable=False)
    subtotal = Column(Numeric(18, 4), default=0.0, nullable=False)
    discount_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    terms_and_conditions = Column(Text, nullable=True)

    customer = relationship("backend.src.modules.accounts_receivable.models.Customer")
    lines = relationship("SalesQuotationLine", back_populates="quotation", cascade="all, delete-orphan")


class SalesQuotationLine(Base):
    """
    Line item on sales quotation.
    """
    __tablename__ = "sales_quotation_lines"

    quotation_id = Column(String(36), ForeignKey("sales_quotations.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Numeric(18, 4), default=1.0, nullable=False)
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(7, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    line_total = Column(Numeric(18, 4), nullable=False)

    quotation = relationship("SalesQuotation", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")


class SalesOrder(Base):
    """
    Customer confirmed Sales Order (SO).
    """
    __tablename__ = "sales_orders"

    so_number = Column(String(50), nullable=False, index=True, doc="e.g. 'SO-2026-0001'")
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    quotation_id = Column(String(36), ForeignKey("sales_quotations.id"), nullable=True)
    
    order_date = Column(Date, nullable=False)
    requested_delivery_date = Column(Date, nullable=False)
    
    currency = Column(String(3), default="USD", nullable=False)
    exchange_rate = Column(Numeric(18, 6), default=1.0, nullable=False)
    
    status = Column(String(30), default="CONFIRMED", nullable=False, index=True, doc="DRAFT, CONFIRMED, PROCESSING, PARTIALLY_FULFILLED, FULFILLED, CANCELLED")
    shipping_address = Column(Text, nullable=True)
    payment_terms_days = Column(Integer, default=30, nullable=False)
    
    subtotal = Column(Numeric(18, 4), default=0.0, nullable=False)
    discount_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    total_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    notes = Column(Text, nullable=True)

    customer = relationship("backend.src.modules.accounts_receivable.models.Customer")
    lines = relationship("SalesOrderLine", back_populates="sales_order", cascade="all, delete-orphan")
    deliveries = relationship("FulfillmentDelivery", back_populates="sales_order")

    __table_args__ = (
        Index("ix_sales_so_tenant_number", "tenant_id", "so_number", unique=True),
    )


class SalesOrderLine(Base):
    """
    Line item on sales order tracking ordered, allocated, fulfilled, and invoiced quantities.
    """
    __tablename__ = "sales_order_lines"

    sales_order_id = Column(String(36), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    description = Column(String(255), nullable=False)
    quantity_ordered = Column(Numeric(18, 4), nullable=False)
    quantity_allocated = Column(Numeric(18, 4), default=0.0, nullable=False, doc="Soft reserved stock")
    quantity_fulfilled = Column(Numeric(18, 4), default=0.0, nullable=False)
    quantity_invoiced = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    unit_price = Column(Numeric(18, 4), nullable=False)
    discount_percent = Column(Numeric(7, 4), default=0.0, nullable=False)
    tax_rate_id = Column(String(36), ForeignKey("fin_tax_rates.id"), nullable=True)
    tax_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    line_total = Column(Numeric(18, 4), nullable=False)

    sales_order = relationship("SalesOrder", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")


class FulfillmentDelivery(Base):
    """
    Pick, Pack, and Ship warehouse dispatch fulfillment.
    """
    __tablename__ = "sales_fulfillment_deliveries"

    delivery_number = Column(String(50), nullable=False, index=True, doc="e.g. 'DLV-2026-0001'")
    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"), nullable=False)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=False)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=False)
    
    dispatch_date = Column(Date, nullable=False)
    carrier = Column(String(100), default="FedEx Ground", nullable=False)
    tracking_number = Column(String(100), nullable=True)
    status = Column(String(30), default="SHIPPED", nullable=False, doc="PICKED, PACKED, SHIPPED, DELIVERED")
    
    stock_movement_id = Column(String(36), ForeignKey("inv_stock_movements.id"), nullable=True)
    notes = Column(Text, nullable=True)

    sales_order = relationship("SalesOrder", back_populates="deliveries")
    lines = relationship("FulfillmentDeliveryLine", back_populates="delivery", cascade="all, delete-orphan")


class FulfillmentDeliveryLine(Base):
    """
    Dispatched items in a fulfillment delivery.
    """
    __tablename__ = "sales_delivery_lines"

    delivery_id = Column(String(36), ForeignKey("sales_fulfillment_deliveries.id", ondelete="CASCADE"), nullable=False)
    so_line_id = Column(String(36), ForeignKey("sales_order_lines.id"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    location_id = Column(String(36), ForeignKey("inv_warehouse_locations.id"), nullable=False)
    quantity_shipped = Column(Numeric(18, 4), nullable=False)

    delivery = relationship("FulfillmentDelivery", back_populates="lines")
    item = relationship("backend.src.modules.inventory.models.Item")
