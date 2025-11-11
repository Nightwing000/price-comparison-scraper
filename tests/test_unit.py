"""
Unit tests for application logic.
These tests do not require a database or live server.
"""

import pytest
from src.app.scraper import ScraperService
from src.app.database import ScrapeTarget

# Mock HTML content for a fake product page
MOCK_HTML = """
<html>
<body>
    <div class="product">
        <h1 class="product-title">Product 1</h1>
        <a class="product-link" href="/product/1">Link 1</a>
        <span class="product-price">$19.99</span>
    </div>
    <div class="product">
        <h1 class="product-title">Product 2</h1>
        <a class="product-link" href="/product/2">Link 2</a>
        <span class="product-price">€25.00</span>
    </div>
    <div class="product">
        <h1 class="product-title">Product 3</h1>
        <!-- Missing price -->
        <a class="product-link" href="/product/3">Link 3</a>
    </div>
</body>
</html>
"""

@pytest.fixture
def mock_target() -> ScrapeTarget:
    """Fixture for a mock ScrapeTarget."""
    return ScrapeTarget(
        id=1,
        name="Mock Store",
        base_url="http://mockstore.com",
        name_selector="h1.product-title",
        price_selector="span.product-price",
        url_selector="a.product-link"
    )

