"""
NexERP Authentication & RBAC Test Suite.
Verifies Bcrypt hashing, JWT token lifecycle, and role permission resolution.
"""

import pytest
from backend.src.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hashing_and_verification():
    """
    Ensure passwords are encrypted with salted Bcrypt and accurately verified.
    """
    raw_password = "SecureEnterprisePassword123!"
    hashed = hash_password(raw_password)

    assert hashed != raw_password
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_generation_and_payload_decoding():
    """
    Ensure JWT access tokens encode tenant isolation, user ID, and claims accurately.
    """
    user_id = "usr_test_999"
    tenant_id = "org_corp_hq_001"
    roles = ["FinanceManager", "Accountant"]
    permissions = ["financials:gl:post", "financials:reports:view"]

    token = create_access_token(
        subject=user_id,
        tenant_id=tenant_id,
        roles=roles,
        permissions=permissions
    )

    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Header.Payload.Signature

    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["tenant_id"] == tenant_id
    assert payload["roles"] == roles
    assert "financials:gl:post" in payload["permissions"]
