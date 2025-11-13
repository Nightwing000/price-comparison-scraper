"""
System tests for end-to-end user flows.
These tests simulate a full workflow.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, MagicMock

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
    # We patch 'httpx.AsyncClient.get'
    with patch("httpx.AsyncClient.get") as mock_get:
        # Create a mock response object
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = SYSTEM_TEST_HTML
        mock_response.raise_for_status = MagicMock()
        
        # Set the mock to return our mock response
        mock_get.return_value = mock_response
        yield mock_get


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
