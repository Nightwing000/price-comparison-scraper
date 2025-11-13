"""
System tests for end-to-end user flows.
These tests simulate a full workflow.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock, AsyncMock

from src.app.core import settings
from src.app import database as db

pytestmark = pytest.mark.asyncio

# Mock HTML for the system test
SYSTEM_TEST_HTML = """
<html>
<body>
    <div class="product-item">
        <h2 class="product-name">E2E Test Widget</h2>
        <a class="product-url" href="/product/e2e-widget">Link</a>
        <div class="product-price">$123.45</div>
    </div>
</body>
</html>
"""


@pytest_asyncio.fixture
def mock_httpx_get():
    """Mocks httpx.AsyncClient.get to return our mock HTML."""
    # We need to patch the AsyncClient class itself
    with patch("httpx.AsyncClient") as mock_client_class:
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SYSTEM_TEST_HTML
        mock_response.raise_for_status = MagicMock()
        
        # Create a mock client instance
        mock_client_instance = MagicMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()
        
        # Set the mock class to return our mock instance
        mock_client_class.return_value = mock_client_instance
        
        yield mock_client_instance.get


async def test_full_e2e_flow(
    api_client: AsyncClient, 
    db_session: AsyncSession, 
    mock_httpx_get
):
    """
    Test the full workflow as required by US-014:
    1. Admin adds a new scrape target.
    2. Admin triggers a manual scrape.
    3. (Mocked) Scraper fetches HTML, parses it, and saves the product.
    4. Client searches for the new product and finds it.
    """
    
    admin_headers = {"x-api-key": settings.ADMIN_API_KEY}
    client_headers = {"x-api-key": settings.CLIENT_API_KEY}

    # --- 1. Admin adds a new scrape target ---
    target_data = {
        "name": "E2E Test Site",
        "base_url": "http://e2e-test-site.com",
        "name_selector": "h2.product-name",
        "price_selector": "div.product-price",
        "url_selector": "a.product-url"
    }
    
    response = await api_client.post(
        "/api/v1/admin/target", 
        json=target_data, 
        headers=admin_headers
    )
    assert response.status_code == 201
    
    # --- 2. Admin triggers a manual scrape ---
    response = await api_client.post(
        "/api/v1/admin/trigger-scrape", 
        headers=admin_headers
    )
    assert response.status_code == 202
    assert response.json() == {"message": "Scraping job triggered successfully."}
    
    # --- 3. Verify (Mocked) Scrape Results ---
    
    # Check that httpx.get was called with the correct URL
    mock_httpx_get.assert_called_with("http://e2e-test-site.com")
    
    # Check the database for the scrape log
    logs = await db.get_latest_scrape_logs(db_session, 1)
    assert len(logs) > 0
    log = logs[0]
    assert log.target_name == "E2E Test Site"
    assert log.status == "success"
    assert log.products_found == 1
    
    # Check the database for the new product
    products = await db.search_products_by_name(db_session, "E2E Test Widget")
    assert len(products) == 1
    product = products[0]
    assert product.name == "E2E Test Widget"
    assert product.price == 123.45
    assert product.url == "http://e2e-test-site.com/product/e2e-widget"
    assert product.source_site == "E2E Test Site"

    # --- 4. Client searches for the new product ---
    response = await api_client.get(
        "/api/v1/search?q=Widget", 
        headers=client_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == "E2E Test Widget"
    assert data[0]['price'] == 123.45
