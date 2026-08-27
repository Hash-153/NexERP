"""
Audit & Forensic Compliance Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class ContinuousControlMonitorRule(Base):
    """Automated robotic rule monitoring general ledger journals for anomalies."""
    __tablename__ = "aud_control_rules"

    rule_code = Column(String(50), nullable=False, unique=True, index=True)
    rule_name = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), default="JOURNAL_ANOMALY", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    threshold_amount = Column(Numeric(14, 4), default=100000.00, nullable=False)


class ForensicAuditExceptionLog(Base):
    """Flagged suspicious or high-risk transaction exception."""
    __tablename__ = "aud_exception_logs"

    rule_id = Column(String(36), ForeignKey("aud_control_rules.id"), nullable=False)
    transaction_reference = Column(String(64), nullable=False, index=True)
    flagged_amount = Column(Numeric(14, 4), nullable=False)
    severity = Column(String(30), default="SIGNIFICANT_DEFICIENCY", nullable=False)
    anomaly_reason = Column(String(255), nullable=False)
    is_investigated = Column(Boolean, default=False, nullable=False)
    investigation_notes = Column(Text, nullable=True)
