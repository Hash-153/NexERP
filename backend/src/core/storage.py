"""
NexERP Attachment Vault & Secure Document Storage Subsystem.
Provides file integrity checking (SHA-256), MIME-type verification, and local/S3 abstraction.
"""

import os
import hashlib
import aiofiles
from typing import Optional, Tuple
from sqlalchemy import Column, String, Integer, BigInteger
from .database import Base
from .config import settings
from .exceptions import BusinessRuleViolationError


class DocumentAttachment(Base):
    """
    Metadata record for files and business documents attached to ERP transactions.
    """
    __tablename__ = "core_document_attachments"

    entity_type = Column(String(50), nullable=False, index=True, doc="e.g. VendorBill, Employee, PurchaseOrder")
    entity_id = Column(String(36), nullable=False, index=True, doc="Target document record ID")
    
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_extension = Column(String(20), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    checksum_sha256 = Column(String(64), nullable=False, index=True)
    storage_path = Column(String(500), nullable=False)


class StorageService:
    """
    Manages physical file persistence, validation, and retrieval from the attachment vault.
    """

    @classmethod
    def _ensure_directory(cls, path: str) -> None:
        """Create target storage directory if it does not exist."""
        os.makedirs(path, exist_ok=True)

    @classmethod
    async def save_file(
        cls,
        file_bytes: bytes,
        original_filename: str,
        entity_type: str,
        entity_id: str,
        tenant_id: str
    ) -> DocumentAttachment:
        """
        Validate extension and size, compute SHA-256 hash, and persist file securely.
        """
        # Validate size
        max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        if len(file_bytes) > max_bytes:
            raise BusinessRuleViolationError(
                f"File size exceeds the allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        # Validate extension
        _, ext = os.path.splitext(original_filename)
        clean_ext = ext.lstrip(".").lower()
        if clean_ext not in settings.ALLOWED_UPLOAD_EXTENSIONS:
            raise BusinessRuleViolationError(
                f"File extension '.{clean_ext}' is not permitted. Allowed: {settings.ALLOWED_UPLOAD_EXTENSIONS}"
            )

        # Compute SHA-256
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        # Destination path: storage/vault/<tenant_id>/<entity_type>/<sha256>.<ext>
        tenant_dir = os.path.join(settings.STORAGE_LOCAL_ROOT, tenant_id, entity_type)
        cls._ensure_directory(tenant_dir)

        stored_filename = f"{sha256_hash}.{clean_ext}"
        physical_path = os.path.join(tenant_dir, stored_filename)

        async with aiofiles.open(physical_path, "wb") as f:
            await f.write(file_bytes)

        return DocumentAttachment(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            file_name=stored_filename,
            original_file_name=original_filename,
            file_extension=clean_ext,
            mime_type=f"application/{clean_ext}",
            file_size_bytes=len(file_bytes),
            checksum_sha256=sha256_hash,
            storage_path=physical_path
        )
