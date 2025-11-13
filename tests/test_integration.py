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
    await db.create_scrape_log(db_session, log)
    
    headers = {"x-api-key": settings.ADMIN_API_KEY}
    response = await api_client.get("/api/v1/admin/logs", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Find our log in the results
    our_log = next((l for l in data if l['target_name'] == "Test Store"), None)
    assert our_log is not None
    assert our_log['status'] == "success"
    assert our_log['products_found'] == 2


async def test_trigger_scrape(api_client: AsyncClient):
    """Test manually triggering a scrape job via API."""
    headers = {"x-api-key": settings.ADMIN_API_KEY}
    response = await api_client.post("/api/v1/admin/trigger-scrape", headers=headers)
    
    # Should return 202 Accepted or 200 OK
    assert response.status_code in [200, 202]
    data = response.json()
    assert "message" in data or "status" in data


async def test_search_no_results(api_client: AsyncClient):
    """Test searching with query that has no results."""
    headers = {"x-api-key": settings.CLIENT_API_KEY}
    response = await api_client.get("/api/v1/search?q=NonexistentProduct123", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == []


async def test_get_logs_empty(api_client: AsyncClient):
    """Test getting logs when none exist for a new test."""
    headers = {"x-api-key": settings.ADMIN_API_KEY}
    response = await api_client.get("/api/v1/admin/logs", headers=headers)
    
    assert response.status_code == 200
    # May or may not be empty depending on test order, but should be valid list
    assert isinstance(response.json(), list)


