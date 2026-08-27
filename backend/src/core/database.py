"""
NexERP Core Database Engine & Declarative Persistence Layer.
Provides Async SQLAlchemy 2.0 engine, multi-tenant aware base models, and session management.
"""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Any, Dict
from sqlalchemy import Column, String, DateTime, Boolean, event
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from .config import settings


class Base(DeclarativeBase):
    """
    Root declarative base for all NexERP domain models.
    Provides standard audit columns, UUID primary keys, and multi-tenant tagging.
    """
    
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Default table name is lowercased class name + 's' if not specified
        return cls.__name__.lower() + "s"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
        doc="Universally unique primary identifier"
    )
    
    tenant_id = Column(
        String(50),
        nullable=False,
        default=lambda: settings.DEFAULT_TENANT_ID,
        index=True,
        doc="Multi-tenant organization boundary key"
    )
    
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="Logical active status flag"
    )
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        doc="Soft-delete flag to preserve audit history"
    )
    
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp of record creation (UTC)"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        doc="Timestamp of last modification (UTC)"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when record was soft-deleted"
    )
    
    created_by_id = Column(
        String(36),
        nullable=True,
        doc="User ID who created the record"
    )
    
    updated_by_id = Column(
        String(36),
        nullable=True,
        doc="User ID who last modified the record"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance into a dictionary representation."""
        result = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, datetime):
                val = val.isoformat()
            result[column.name] = val
        return result

    def soft_delete(self, user_id: str = None) -> None:
        """Mark record as soft-deleted without physically removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        if user_id:
            self.updated_by_id = user_id


# Initialize Async Engine with connection pool parameters
_engine_kwargs = {
    "echo": settings.DATABASE_ECHO,
    "future": True,
}

if "sqlite" in settings.DATABASE_URL:
    # SQLite does not support pool_size / max_overflow
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    _engine_kwargs["pool_size"] = settings.DATABASE_POOL_SIZE
    _engine_kwargs["max_overflow"] = settings.DATABASE_MAX_OVERFLOW
    _engine_kwargs["pool_timeout"] = settings.DATABASE_POOL_TIMEOUT
    _engine_kwargs["pool_pre_ping"] = True

async_engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **_engine_kwargs
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def init_db_engine() -> None:
    """Create all database schema tables if they do not exist."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an isolated async database session per request.
    Rolls back transaction automatically if an exception occurs during request execution.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
