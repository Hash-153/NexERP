"""
Advanced Planning & Scheduling Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class WorkCenterResourceCreate(BaseModel):
    code: str
    name: str
    plant_facility_id: str
    department: str
    daily_shift_hours: Decimal = Decimal("16.0")
    number_of_machines: int = 1
    hourly_standard_cost: Decimal = Decimal("85.00")
    is_bottleneck_critical: bool = False

class ScheduledOperationInput(BaseModel):
    work_center_id: str
    work_order_number: str
    operation_sequence: int = 10
    operation_name: str
    setup_hours: Decimal
    run_hours: Decimal
    planned_start_time: datetime
