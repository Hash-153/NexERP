"""
Tax Engine Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class TaxJurisdictionRule(Base):
    """Statutory tax rate rule by country, state, county, and city jurisdiction."""
    __tablename__ = "tax_jurisdiction_rules"

    country_code = Column(String(3), nullable=False, index=True)  # US, GB, DE, CA
    state_province = Column(String(50), nullable=True, index=True)
    county_name = Column(String(100), nullable=True)
    city_name = Column(String(100), nullable=True)
    postal_code_prefix = Column(String(20), nullable=True, index=True)
    
    tax_type = Column(String(40), default="US_SALES_USE_TAX", nullable=False)
    state_rate = Column(Numeric(8, 6), default=0.0, nullable=False)
    county_rate = Column(Numeric(8, 6), default=0.0, nullable=False)
    city_rate = Column(Numeric(8, 6), default=0.0, nullable=False)
    special_district_rate = Column(Numeric(8, 6), default=0.0, nullable=False)
    combined_effective_rate = Column(Numeric(8, 6), nullable=False)
    
    effective_start_date = Column(Date, nullable=False)
    effective_end_date = Column(Date, nullable=True)
    is_active_rule = Column(Boolean, default=True, nullable=False)


class TaxExemptionCertificate(Base):
    """Customer resale, non-profit, or government exemption certificate."""
    __tablename__ = "tax_exemption_certificates"

    customer_account_id = Column(String(36), nullable=False, index=True)
    certificate_number = Column(String(100), nullable=False, index=True)
    exemption_reason = Column(String(50), nullable=False)  # RESALE, NON_PROFIT_501C3, GOVERNMENT, MANUFACTURING_EQUIPMENT
    issuing_state_or_country = Column(String(50), nullable=False)
    
    effective_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verified_by_user_id = Column(String(36), nullable=True)
    document_attachment_url = Column(String(255), nullable=True)
