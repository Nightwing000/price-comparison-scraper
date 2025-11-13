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
    
    # Create products
    p1 = db.Product(
        name="Test Product Alpha",
        price=10.00,
        url="http://test.com/1",
        source_site="Test Store"
    )
    p2 = db.Product(
        name="Test Product Bravo",
        price=20.00,
        url="http://test.com/2",
        source_site="Test Store"
    )
    db_session.add_all([p1, p2])
    await db_session.commit()
    
    return {"target": target, "products": [p1, p2]}

# --- Test API Security ---

@pytest.mark.parametrize("endpoint", ["/api/v1/search?q=test", "/api/v1/admin/logs"])
async def test_missing_api_key(api_client: AsyncClient, endpoint: str):
    """Test that endpoints fail without an API key."""
    response = await api_client.get(endpoint)
    assert response.status_code == 401
    assert "missing" in response.json()['detail'].lower()