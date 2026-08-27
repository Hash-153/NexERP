"""
NexERP Pytest Conftest Test Harness & Fixtures.
Configures isolated in-memory test database, test client, and authenticated SuperAdmin session.
"""

import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.src.core.database import Base, get_db_session
from backend.src.core.security import create_access_token, hash_password
from backend.src.main import app
from backend.src.modules.auth.models import Tenant, User, Role, UserRole

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create all tables in fresh in-memory database and yield transaction session.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        # Seed Base Tenant
        tenant = Tenant(
            id="org_corp_hq_001",
            name="Apex Dynamics Industrial Corp (Test)",
            code="APEX-TEST",
            currency="USD",
            tax_identifier="EIN-88-2918291",
            country="United States",
            timezone="America/New_York",
            fiscal_year_start_month="January",
            is_active=True
        )
        session.add(tenant)
        await session.flush()

        # Seed SuperAdmin User
        admin_role = Role(tenant_id="org_corp_hq_001", name="SuperAdmin", is_system_role=True)
        session.add(admin_role)
        await session.flush()

        admin_user = User(
            id="usr_admin_001",
            tenant_id="org_corp_hq_001",
            email="admin@apexdynamics.com",
            hashed_password=hash_password("AdminPass123!"),
            first_name="Alexander",
            last_name="Vance",
            is_superuser=True,
            is_active=True
        )
        session.add(admin_user)
        await session.flush()

        session.add(UserRole(tenant_id="org_corp_hq_001", user_id=admin_user.id, role_id=admin_role.id))
        await session.commit()

        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    FastAPI Async Test Client with dependency injection override and pre-authenticated Bearer Token.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = override_get_db

    token = create_access_token(
        subject="usr_admin_001",
        tenant_id="org_corp_hq_001",
        roles=["SuperAdmin"],
        permissions=["admin:all", "*"]
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver", headers={"Authorization": f"Bearer {token}"}) as ac:
        yield ac

    app.dependency_overrides.clear()
