"""
NexERP Projects Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from .enums import BillingType, ProjectStatus, TaskPriority, TaskStatus, TimesheetStatus


# Project Schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    customer_id: Optional[str] = None
    manager_id: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    budget_amount: Decimal = Field(default=Decimal("0.0"), ge=0)
    billing_type: BillingType = BillingType.TIME_AND_MATERIALS
    currency: str = "USD"
    notes: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: str
    tenant_id: str
    project_number: str
    status: ProjectStatus
    total_logged_hours: Decimal
    total_cost_incurred: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# Milestone Schemas
class MilestoneCreate(BaseModel):
    name: str
    due_date: date
    billing_amount: Decimal = Field(default=Decimal("0.0"), ge=0)


class MilestoneResponse(BaseModel):
    id: str
    project_id: str
    name: str
    due_date: date
    billing_amount: Decimal
    is_completed: bool
    is_invoiced: bool

    class Config:
        from_attributes = True


# Task Schemas
class TaskCreate(BaseModel):
    project_id: str
    milestone_id: Optional[str] = None
    title: str = Field(..., min_length=2, max_length=200)
    description: Optional[str] = None
    assigned_to_id: Optional[str] = None
    estimated_hours: Decimal = Field(default=Decimal("0.0"), ge=0)
    priority: TaskPriority = TaskPriority.MEDIUM
    start_date: Optional[date] = None
    due_date: Optional[date] = None


class TaskResponse(BaseModel):
    id: str
    tenant_id: str
    project_id: str
    milestone_id: Optional[str]
    task_number: str
    title: str
    description: Optional[str]
    assigned_to_id: Optional[str]
    estimated_hours: Decimal
    actual_hours: Decimal
    priority: TaskPriority
    status: TaskStatus
    start_date: Optional[date]
    due_date: Optional[date]
    created_at: datetime

    class Config:
        from_attributes = True


# Timesheet Schemas
class TimesheetEntryCreate(BaseModel):
    project_id: str
    task_id: Optional[str] = None
    work_date: date
    hours: Decimal = Field(..., gt=0, le=24)
    hourly_billing_rate: Decimal = Field(default=Decimal("125.0"), ge=0)
    is_billable: bool = True
    description: Optional[str] = None


class TimesheetEntryResponse(BaseModel):
    id: str
    project_id: str
    task_id: Optional[str]
    work_date: date
    hours: Decimal
    hourly_billing_rate: Decimal
    is_billable: bool
    is_invoiced: bool
    description: Optional[str]

    class Config:
        from_attributes = True


class TimesheetCreate(BaseModel):
    employee_id: str
    period_start_date: date
    period_end_date: date
    entries: List[TimesheetEntryCreate] = Field(..., min_length=1)


class TimesheetResponse(BaseModel):
    id: str
    tenant_id: str
    timesheet_number: str
    employee_id: str
    period_start_date: date
    period_end_date: date
    total_hours: Decimal
    status: TimesheetStatus
    entries: List[TimesheetEntryResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True
