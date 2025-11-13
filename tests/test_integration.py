"""
Integration tests for API endpoints and database.
Uses the test database fixtures from conftest.py.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core import settings
from src.app import database as db

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture(scope="function")
async def setup_test_data(db_session: AsyncSession):
    """Seed the test database with some data."""
    # Create a target
    target = db.ScrapeTarget(
        id=1,
        name="Test Store",
        base_url="http://test.com",
        name_selector="h1",
        price_selector="span",
        url_selector="a"
    )
    db_session.add(target)