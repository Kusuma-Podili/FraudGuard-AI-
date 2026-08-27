"""Pytest Fixtures, Mock In-Memory Database, and Test Clients."""

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from backend.app.db.base import Base
from backend.app.core.security import create_access_token
from backend.app.models.user import User, UserRole

# Use in-memory SQLite for high-speed testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def auth_token_analyst() -> str:
    return create_access_token(subject="USR_ANALYST_01", role="FRAUD_ANALYST")


@pytest.fixture
def auth_token_admin() -> str:
    return create_access_token(subject="USR_ADMIN_01", role="ADMIN")
