"""
Pytest fixtures for testing.
"""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.app.main import app
from src.app.database import Base, get_db
from src.app.core import settings

# --- Test Database Setup ---
# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create a new async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}, # Required for SQLite
)

# Create a new sessionmaker for testing
TestingSessionLocal = async_sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=test_engine,
    class_=AsyncSession
)

# --- Fixtures ---

@pytest_asyncio.fixture(scope="session")
async def db_engine():
    """
    Fixture for the test database engine.
    Creates all tables before tests run, drops them after.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_engine
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture for a test database session.
    Each test gets a fresh session and transaction that's rolled back after.
    """
    connection = await db_engine.connect()
    transaction = await connection.begin()
    
    session = AsyncSession(bind=connection, expire_on_commit=False)
    
    yield session
    
    await session.close()
    await transaction.rollback()
    await connection.close()

@pytest_asyncio.fixture(scope="function")
async def api_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture for an async test client.
    Overrides the `get_db` dependency to use the test session.
    """
    def override_get_db():
        """Override get_db dependency."""
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    
    del app.dependency_overrides[get_db]
