"""
Alembic environment configuration for NexERP.
Supports both sync (offline) and async (online) migration modes.
"""

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Import NexERP SQLAlchemy Base and all model modules to ensure tables are registered
from backend.src.core.database import Base  # noqa: F401

# Import all model modules to register them in Base.metadata
import backend.src.modules.auth.models  # noqa: F401
import backend.src.modules.financials.models  # noqa: F401
import backend.src.modules.accounts_payable.models  # noqa: F401
import backend.src.modules.accounts_receivable.models  # noqa: F401
import backend.src.modules.inventory.models  # noqa: F401
import backend.src.modules.procurement.models  # noqa: F401
import backend.src.modules.sales.models  # noqa: F401
import backend.src.modules.manufacturing.models  # noqa: F401
import backend.src.modules.quality_control.models  # noqa: F401
import backend.src.modules.human_resources.models  # noqa: F401
import backend.src.modules.projects.models  # noqa: F401
import backend.src.modules.governance.models  # noqa: F401

# Alembic config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with DATABASE_URL environment variable if set
database_url = os.getenv("DATABASE_URL")
if database_url:
    # Convert asyncpg URLs for Alembic (uses sync psycopg2 for migrations)
    sync_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    config.set_main_option("sqlalchemy.url", sync_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode without a live DB connection.
    Generates SQL script output only.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Execute migrations within a running database connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Run migrations against a live async PostgreSQL / SQLite connection.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode with a live database connection."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
