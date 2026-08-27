"""Security administration records for API access, login audits, and feature flags."""

from sqlalchemy import Boolean, Column, DateTime, Index, String, Text
from backend.src.core.database import Base


class APIKey(Base):
    __tablename__ = "auth_api_keys"
    __table_args__ = (Index("ix_auth_api_key_hash", "key_hash", unique=True),)
    name = Column(String(120), nullable=False)
    key_hash = Column(String(128), nullable=False)
    key_prefix = Column(String(16), nullable=False)
    scopes = Column(Text, nullable=False, default="[]")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_by_id = Column(String(36), nullable=False)


class LoginAudit(Base):
    __tablename__ = "auth_login_audits"
    user_id = Column(String(36), nullable=True)
    email = Column(String(255), nullable=True)
    event_type = Column(String(30), nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(500), nullable=True)
    failure_reason = Column(String(255), nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False)


class TenantFeatureFlag(Base):
    __tablename__ = "auth_tenant_feature_flags"
    __table_args__ = (Index("ix_auth_feature_tenant_code", "tenant_id", "feature_code", unique=True),)
    feature_code = Column(String(80), nullable=False)
    enabled = Column(Boolean, nullable=False, default=False)
    rollout_percent = Column(String(5), nullable=False, default="100")
    description = Column(Text, nullable=True)
    updated_by_id = Column(String(36), nullable=True)
