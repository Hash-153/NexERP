"""
NexERP Quality Control (QC), AQL Sampling & CAPA Database Models.
Handles Inspection Checklists, Parameter Evaluations, Non-Conformance Reports (NCR), and Corrective Actions.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index, JSON
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class QualityInspectionPlan(Base):
    """
    Quality inspection template plan with sample sizing and test specs.
    """
    __tablename__ = "qc_inspection_plans"

    code = Column(String(50), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=True)
    inspection_type = Column(String(30), default="INCOMING_RECEIPT", nullable=False, doc="INCOMING_RECEIPT, IN_PROCESS, FINAL_DISPATCH")
    sample_size_percentage = Column(Numeric(5, 2), default=10.0, nullable=False)
    pass_threshold_percentage = Column(Numeric(5, 2), default=95.0, nullable=False)

    item = relationship("backend.src.modules.inventory.models.Item")
    parameters = relationship("QualityParameter", back_populates="plan", cascade="all, delete-orphan")


class QualityParameter(Base):
    """
    Specific inspection testing criterion (numeric tolerance range or boolean pass/fail).
    """
    __tablename__ = "qc_parameters"

    inspection_plan_id = Column(String(36), ForeignKey("qc_inspection_plans.id", ondelete="CASCADE"), nullable=False)
    parameter_name = Column(String(150), nullable=False)
    test_type = Column(String(30), default="NUMERIC_RANGE", nullable=False, doc="NUMERIC_RANGE, PASS_FAIL, TEXT_MATCH")
    
    min_value = Column(Numeric(18, 4), nullable=True)
    max_value = Column(Numeric(18, 4), nullable=True)
    target_value = Column(String(100), nullable=True)
    is_critical = Column(Boolean, default=False, nullable=False, doc="Critical defects cause immediate lot rejection")

    plan = relationship("QualityInspectionPlan", back_populates="parameters")


class InspectionRecord(Base):
    """
    Forensic QA/QC audit report capturing test measurements and pass/fail verdicts.
    """
    __tablename__ = "qc_inspection_records"

    inspection_number = Column(String(50), nullable=False, index=True, doc="e.g. 'QC-2026-0001'")
    plan_id = Column(String(36), ForeignKey("qc_inspection_plans.id"), nullable=False)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    
    source_document_type = Column(String(50), nullable=True, doc="GoodsReceiptNote, ProductionOrder")
    source_document_id = Column(String(36), nullable=True)
    
    inspection_date = Column(Date, nullable=False)
    inspector_id = Column(String(36), nullable=True)
    
    inspected_quantity = Column(Numeric(18, 4), nullable=False)
    passed_quantity = Column(Numeric(18, 4), nullable=False)
    rejected_quantity = Column(Numeric(18, 4), default=0.0, nullable=False)
    status = Column(String(30), default="PASS", nullable=False, doc="PASS, FAIL, CONDITIONAL")
    remarks = Column(Text, nullable=True)

    plan = relationship("QualityInspectionPlan")
    item = relationship("backend.src.modules.inventory.models.Item")
    results = relationship("InspectionResultLine", back_populates="inspection", cascade="all, delete-orphan")


class InspectionResultLine(Base):
    """
    Parameter test result record.
    """
    __tablename__ = "qc_inspection_results"

    inspection_record_id = Column(String(36), ForeignKey("qc_inspection_records.id", ondelete="CASCADE"), nullable=False)
    parameter_id = Column(String(36), ForeignKey("qc_parameters.id"), nullable=False)
    
    measured_numeric_value = Column(Numeric(18, 4), nullable=True)
    pass_fail_result = Column(Boolean, default=True, nullable=False)
    is_conforming = Column(Boolean, default=True, nullable=False)
    remarks = Column(String(255), nullable=True)

    inspection = relationship("InspectionRecord", back_populates="results")
    parameter = relationship("QualityParameter")


class NonConformanceReport(Base):
    """
    Non-Conformance Report (NCR) and Corrective / Preventive Action (CAPA) tracking record.
    """
    __tablename__ = "qc_non_conformance_reports"

    ncr_number = Column(String(50), nullable=False, index=True, doc="e.g. 'NCR-2026-0001'")
    inspection_record_id = Column(String(36), ForeignKey("qc_inspection_records.id"), nullable=True)
    item_id = Column(String(36), ForeignKey("inv_items.id"), nullable=False)
    
    issue_summary = Column(String(255), nullable=False)
    root_cause_analysis = Column(Text, nullable=True, doc="5-Whys / Fishbone analysis")
    containment_action = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    
    status = Column(String(30), default="OPEN", nullable=False, doc="OPEN, UNDER_INVESTIGATION, CAPA_PENDING, CLOSED")
    assigned_to_id = Column(String(36), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    item = relationship("backend.src.modules.inventory.models.Item")
