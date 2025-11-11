"""
Pytest fixtures for testing.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.app.main import app
from src.app.database import Base

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

