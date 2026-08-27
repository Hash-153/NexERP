"""
NexERP Project Management, Work Breakdown Structure (WBS) & Timesheet Database Models.
Handles Project Scheduling, Milestones, Task Dependencies, Employee Timesheet Tracking, and Billable Costing.
"""

from decimal import Decimal
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean, Date, DateTime, Integer, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from backend.src.core.database import Base


class Project(Base):
    """
    Project entity tracking scope, budget, schedule, and contract billing structure.
    """
    __tablename__ = "pm_projects"

    project_number = Column(String(50), nullable=False, index=True, doc="e.g. 'PRJ-2026-0001'")
    name = Column(String(200), nullable=False)
    customer_id = Column(String(36), ForeignKey("ar_customers.id"), nullable=True)
    manager_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    budget_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    billing_type = Column(String(30), default="TIME_AND_MATERIALS", nullable=False, doc="TIME_AND_MATERIALS, FIXED_PRICE")
    currency = Column(String(3), default="USD", nullable=False)
    
    status = Column(String(30), default="ACTIVE", nullable=False, doc="PLANNED, ACTIVE, ON_HOLD, COMPLETED, CANCELLED")
    total_logged_hours = Column(Numeric(10, 2), default=0.0, nullable=False)
    total_cost_incurred = Column(Numeric(18, 4), default=0.0, nullable=False)
    
    notes = Column(Text, nullable=True)

    customer = relationship("backend.src.modules.accounts_receivable.models.Customer")
    manager = relationship("backend.src.modules.human_resources.models.Employee")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Milestone(Base):
    """
    Project phase or deliverable milestone.
    """
    __tablename__ = "pm_milestones"

    project_id = Column(String(36), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    due_date = Column(Date, nullable=False)
    billing_amount = Column(Numeric(18, 4), default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    is_invoiced = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="milestones")


class Task(Base):
    """
    Work Breakdown Structure (WBS) activity task.
    """
    __tablename__ = "pm_tasks"

    project_id = Column(String(36), ForeignKey("pm_projects.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(String(36), ForeignKey("pm_milestones.id"), nullable=True)
    parent_task_id = Column(String(36), ForeignKey("pm_tasks.id"), nullable=True)
    
    task_number = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    assigned_to_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=True)
    estimated_hours = Column(Numeric(7, 2), default=0.0, nullable=False)
    actual_hours = Column(Numeric(7, 2), default=0.0, nullable=False)
    
    priority = Column(String(20), default="MEDIUM", nullable=False, doc="LOW, MEDIUM, HIGH, URGENT")
    status = Column(String(30), default="TODO", nullable=False, doc="TODO, IN_PROGRESS, REVIEW, DONE")
    
    start_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)

    project = relationship("Project", back_populates="tasks")
    assigned_to = relationship("backend.src.modules.human_resources.models.Employee")


class Timesheet(Base):
    """
    Weekly employee timesheet container.
    """
    __tablename__ = "pm_timesheets"

    timesheet_number = Column(String(50), nullable=False, index=True, doc="e.g. 'TS-2026-W05'")
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False)
    period_start_date = Column(Date, nullable=False)
    period_end_date = Column(Date, nullable=False)
    
    total_hours = Column(Numeric(6, 2), default=0.0, nullable=False)
    status = Column(String(30), default="SUBMITTED", nullable=False, doc="DRAFT, SUBMITTED, APPROVED, REJECTED")
    approved_by_id = Column(String(36), nullable=True)

    employee = relationship("backend.src.modules.human_resources.models.Employee")
    entries = relationship("TimesheetEntry", back_populates="timesheet", cascade="all, delete-orphan")


class TimesheetEntry(Base):
    """
    Daily time log row against a project and task.
    """
    __tablename__ = "pm_timesheet_entries"

    timesheet_id = Column(String(36), ForeignKey("pm_timesheets.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(String(36), ForeignKey("pm_projects.id"), nullable=False)
    task_id = Column(String(36), ForeignKey("pm_tasks.id"), nullable=True)
    
    work_date = Column(Date, nullable=False)
    hours = Column(Numeric(5, 2), nullable=False)
    hourly_billing_rate = Column(Numeric(18, 4), default=125.0, nullable=False)
    
    is_billable = Column(Boolean, default=True, nullable=False)
    is_invoiced = Column(Boolean, default=False, nullable=False)
    description = Column(String(255), nullable=True)

    timesheet = relationship("Timesheet", back_populates="entries")
    project = relationship("Project")
    task = relationship("Task")
