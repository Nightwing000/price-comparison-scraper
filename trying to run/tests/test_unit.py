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

def test_parser_extracts_data(mock_target: ScrapeTarget):
    """
    Test that the parser correctly extracts data from mock HTML.
    """
    service = ScraperService(mock_target)
    products = service.parse_html(MOCK_HTML)
    
    # It should find 2 products, as the 3rd is missing a price
    assert len(products) == 2
    
    # Check Product 1
    assert products[0]['name'] == "Product 1"
    assert products[0]['price'] == 19.99
    assert products[0]['url'] == "http://mockstore.com/product/1" # Test URL cleaning
    assert products[0]['source_site'] == "Mock Store"
    
    # Check Product 2
    assert products[1]['name'] == "Product 2"
    assert products[1]['price'] == 25.00 # Test price cleaning
    assert products[1]['url'] == "http://mockstore.com/product/2"

def test_clean_price():
    """Test the price cleaning utility function."""
    service = ScraperService(ScrapeTarget()) # Doesn't need a real target
    
    assert service._clean_price("$19.99") == 19.99
    assert service._clean_price("€25,00") == 25.00
    assert service._clean_price("Free") == 0.0
    assert service._clean_price("1,200.50 USD") == 1200.50

def test_clean_url(mock_target: ScrapeTarget):
    """Test the URL cleaning utility function."""
    service = ScraperService(mock_target)
    
    assert service._clean_url("/product/123") == "http://mockstore.com/product/123"
    assert service._clean_url("http://external.com/product/456") == "http://external.com/product/456"
    assert service._clean_url("page2.html") == "page2.html"
