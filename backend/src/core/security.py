"""
NexERP Cryptographic Security & Authentication Subsystem.
Handles password hashing, JWT claims signing/verification, and API key cryptography.
"""

import hmac
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Union
import bcrypt
from jose import jwt, JWTError
from .config import settings
from .exceptions import UnauthorizedError


def hash_password(password: str) -> str:
    """Hash a plaintext password with salt using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(
    subject: Union[str, Any],
    tenant_id: str,
    roles: list = None,
    permissions: list = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a signed JWT access token containing user identity and authorization claims.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "roles": roles or [],
        "permissions": permissions or [],
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    subject: Union[str, Any],
    tenant_id: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Generate a long-lived signed JWT refresh token for session renewals.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "tenant_id": str(tenant_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": secrets.token_hex(16)
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token signature and expiration.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as exc:
        raise UnauthorizedError(
            message="Invalid or expired authentication token.",
            details={"original_error": str(exc)}
        )


decode_access_token = decode_token


def generate_secure_api_key(prefix: str = "nex_") -> tuple[str, str]:
    """
    Generates a secure API key pair: the raw client key and its SHA-256 hash for database storage.
    """
    raw_key = f"{prefix}{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return raw_key, key_hash


def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    """
    Verify an API key using constant-time comparison to prevent timing attacks.
    """
    computed_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    return hmac.compare_digest(computed_hash, stored_hash)
