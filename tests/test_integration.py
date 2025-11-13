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


async def test_invalid_client_api_key(api_client: AsyncClient):
    """Test client endpoint with an invalid key."""
    headers = {"x-api-key": "wrong_key"}
    response = await api_client.get("/api/v1/search?q=test", headers=headers)
    assert response.status_code == 401
    assert "invalid" in response.json()['detail'].lower()

async def test_invalid_admin_api_key(api_client: AsyncClient):
    """Test admin endpoint with an invalid key."""
    headers = {"x-api-key": "wrong_key"}
    response = await api_client.get("/api/v1/admin/logs", headers=headers)
    assert response.status_code == 401
    assert "invalid" in response.json()['detail'].lower()

# --- Test Client Endpoints ---

async def test_search_product(api_client: AsyncClient, setup_test_data):
    """Test the /search endpoint."""
    headers = {"x-api-key": settings.CLIENT_API_KEY}
    
    # Search for "Alpha"
    response = await api_client.get("/api/v1/search?q=Alpha", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == "Test Product Alpha"
    assert data[0]['price'] == 10.00

    # Search for "Product" (should match both)
    response = await api_client.get("/api/v1/search?q=Product", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Search for "Charlie" (no match)
    response = await api_client.get("/api/v1/search?q=Charlie", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 0

# --- Test Admin Endpoints ---

async def test_add_scrape_target(api_client: AsyncClient, db_session: AsyncSession):
    """Test adding a new scrape target via the admin API."""
    headers = {"x-api-key": settings.ADMIN_API_KEY}
    target_data = {
        "name": "New Store",
        "base_url": "http://newstore.com",
        "name_selector": ".title",
        "price_selector": ".price",
        "url_selector": ".link"
    }
    
    response = await api_client.post("/api/v1/admin/target", json=target_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data['name'] == "New Store"
    assert data['id'] is not None

    # Verify it's in the database
    new_target = await db_session.get(db.ScrapeTarget, data['id'])
    assert new_target is not None
    assert new_target.name == "New Store"

async def test_get_scrape_logs(api_client: AsyncClient, setup_test_data, db_session: AsyncSession):
    """Test retrieving scrape logs."""
    # Add a log
    log = db.ScrapeLog(
        target_name="Test Store",
        status="success",
        products_found=2
    )
    db_session.add(log)
    await db_session.commit()
    
    headers = {"x-api-key": settings.ADMIN_API_KEY}
    response = await api_client.get("/api/v1/admin/logs", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['target_name'] == "Test Store"
    assert data[0]['status'] == "success"
    assert data[0]['products_found'] == 2