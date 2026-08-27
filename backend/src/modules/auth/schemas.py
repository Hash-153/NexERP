"""
NexERP Auth Module Pydantic Data Transfer Schemas.
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# Authentication DTOs
class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    tenant_id: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# Tenant DTOs
class TenantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: str = Field(..., min_length=2, max_length=30)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    tax_identifier: Optional[str] = None
    country: str = "United States"
    timezone: str = "UTC"


class TenantResponse(BaseModel):
    id: str
    name: str
    code: str
    currency: str
    tax_identifier: Optional[str]
    country: str
    timezone: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# User DTOs
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    role_ids: Optional[List[str]] = []
    is_superuser: bool = False


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[str]] = None


class UserResponse(BaseModel):
    id: str
    tenant_id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str]
    is_superuser: bool
    is_active: bool
    roles: List[str] = []
    permissions: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Role & Permission DTOs
class PermissionResponse(BaseModel):
    id: str
    code: str
    module: str
    description: Optional[str]

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    permission_ids: List[str] = []


class RoleResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    is_system_role: bool
    permissions: List[PermissionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()
