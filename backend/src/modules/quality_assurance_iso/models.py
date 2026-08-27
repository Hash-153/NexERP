"""
Quality Assurance ISO Database Models.
"""
from decimal import Decimal
from sqlalchemy import Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from backend.src.core.database import Base

class FMEAFailureModeRecord(Base):
    """Design or Process Failure Mode and Effects Analysis (DFMEA / PFMEA) register."""
    __tablename__ = "qa_fmea_records"

    item_sku = Column(String(50), nullable=False, index=True)
    process_step = Column(String(100), nullable=False)
    potential_failure_mode = Column(String(200), nullable=False)
    potential_effect_of_failure = Column(Text, nullable=False)
    
    severity_rating_s = Column(Integer, default=5, nullable=False)     # 1 - 10
    occurrence_rating_o = Column(Integer, default=4, nullable=False)   # 1 - 10
    detection_rating_d = Column(Integer, default=3, nullable=False)    # 1 - 10
    rpn_risk_priority_number = Column(Integer, nullable=False)        # S * O * D (1 - 1000)
    
    recommended_action = Column(Text, nullable=True)
    is_action_completed = Column(Boolean, default=False, nullable=False)


class PPAPSubmissionPackage(Base):
    """Production Part Approval Process (PPAP) level 1-5 submission dossier."""
    __tablename__ = "qa_ppap_submissions"

    part_number = Column(String(50), nullable=False, index=True)
    customer_account_id = Column(String(36), nullable=False)
    ppap_level = Column(String(20), default="LEVEL_3", nullable=False)
    status = Column(String(30), default="SUBMITTED", nullable=False)  # SUBMITTED, APPROVED, INTERIM_APPROVAL, REJECTED
    psw_part_submission_warrant_signed = Column(Boolean, default=False, nullable=False)
    dimensional_results_passed = Column(Boolean, default=True, nullable=False)
    cpk_process_capability_score = Column(Numeric(5, 2), default=1.67, nullable=False)
