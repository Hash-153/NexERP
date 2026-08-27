"""
Field Service Pydantic Schemas.
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ServiceTechnicianCreate(BaseModel):
    user_id: str
    employee_code: str
    full_name: str
    primary_phone: str
    home_base_location: str
    skills: List[str] = []

class FieldWorkOrderCreate(BaseModel):
    customer_account_id: str
    site_location_address: str
    asset_serial_number: Optional[str] = None
    priority: str = "MEDIUM"
    sla_severity: str = "P2_NEXT_BUSINESS_DAY"
    scheduled_start: datetime
    scheduled_end: datetime
    issue_description: str

class DispatchAssignRequest(BaseModel):
    work_order_id: str
    technician_id: str

class RecordPartUsageRequest(BaseModel):
    work_order_id: str
    item_id: str
    part_number: str
    part_name: str
    quantity: Decimal = Decimal("1.0")
    unit_cost: Decimal
    is_warranty: bool = False
