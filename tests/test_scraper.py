"""
Tests for scraper functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.app.scraper import ScraperService, run_all_scrapes
from src.app.database import ScrapeTarget, ScrapeLog, Product
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio


def test_clean_price_various_formats():
    """Test _clean_price with various price formats."""
    service = ScraperService(ScrapeTarget())
    
    # US format
    assert service._clean_price("$19.99") == 19.99
    assert service._clean_price("$1,234.56") == 1234.56
    
    # European format
    assert service._clean_price("€25,00") == 25.00
    assert service._clean_price("€1.234,56") == 1234.56
    
    # Edge cases
    assert service._clean_price("Free") == 0.0
    assert service._clean_price("") == 0.0
    assert service._clean_price("Price: $99") == 99.0
    assert service._clean_price("10") == 10.0
    
    # Mixed separators - US format (comma as thousands separator)
    assert service._clean_price("1,200.50 USD") == 1200.50
    assert service._clean_price("$2,999.99") == 2999.99


def test_clean_url_relative():
    """Test _clean_url with relative URLs."""
    target = ScrapeTarget(base_url="http://example.com")
    service = ScraperService(target)
    
    assert service._clean_url("/product/123") == "http://example.com/product/123"
    assert service._clean_url("/items/phone") == "http://example.com/items/phone"


def test_clean_url_absolute():
    """Test _clean_url with absolute URLs."""
    target = ScrapeTarget(base_url="http://example.com")
    service = ScraperService(target)
    
    assert service._clean_url("http://external.com/item") == "http://external.com/item"
    assert service._clean_url("https://another.com/page") == "https://another.com/page"


def test_clean_url_relative_no_slash():
    """Test _clean_url with relative URLs without leading slash."""
    target = ScrapeTarget(base_url="http://example.com")
    service = ScraperService(target)
    
    # This should return as-is since it doesn't start with /
    assert service._clean_url("page.html") == "page.html"


def test_parse_html_missing_price():
    """Test parsing HTML where some products are missing prices."""
    html = """
    <html>
    <body>
        <div class="product">
            <h1>Product 1</h1>
            <a href="/p1">Link</a>
            <span class="price">$10.00</span>
        </div>
        <div class="product">
            <h1>Product 2</h1>
            <a href="/p2">Link</a>
            <!-- No price -->
        </div>
    </body>
    </html>
    """
    
    target = ScrapeTarget(
        name="Test Store",
        base_url="http://test.com",
        name_selector="h1",
        price_selector="span.price",
        url_selector="a"
    )
    service = ScraperService(target)
    products = service.parse_html(html)
    
    # Should only return products with all required fields
    assert len(products) == 1
    assert products[0]['name'] == "Product 1"
    assert products[0]['price'] == 10.0


def test_parse_html_invalid():
    """Test parsing invalid HTML."""
    target = ScrapeTarget(
        name="Test",
        base_url="http://test.com",
        name_selector="h1",
        price_selector="span",
        url_selector="a"
    )
    service = ScraperService(target)
    
    # Invalid HTML should return empty list
    products = service.parse_html("not valid html at all!!!")
    assert products == []


def test_parse_html_complete():
    """Test parsing HTML with multiple complete products."""
    html = """
    <html>
    <body>
        <div>
            <h1>Laptop Pro</h1>
            <span class="price">$1,299.99</span>
            <a href="/laptop-pro">View</a>
        </div>
        <div>
            <h1>Tablet Max</h1>
            <span class="price">€899,00</span>
            <a href="/tablet-max">View</a>
        </div>
    </body>
    </html>
    """
    
    target = ScrapeTarget(
        name="Tech Store",
        base_url="http://techstore.com",
        name_selector="h1",
        price_selector="span.price",
        url_selector="a"
    )
    service = ScraperService(target)
    products = service.parse_html(html)
    
    assert len(products) == 2
    assert products[0]['name'] == "Laptop Pro"
    assert products[0]['price'] == 1299.99
    assert products[1]['name'] == "Tablet Max"
    assert products[1]['price'] == 899.0


async def test_fetch_html_with_real_service():
    """Test fetch_html creates and closes httpx client properly."""
    target = ScrapeTarget(
        name="Test Store",
        base_url="http://test.example",
        name_selector="h1",
        price_selector="span",
        url_selector="a"
    )
    service = ScraperService(target)
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test</body></html>"
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_instance.aclose = AsyncMock()
        mock_client_class.return_value = mock_client_instance
        
        # Re-create service to use mocked client
        service = ScraperService(target)
        html = await service.fetch_html()
        
        assert html == "<html><body>Test</body></html>"
        mock_client_instance.aclose.assert_called_once()


async def test_run_all_scrapes_with_successful_scrape(db_session: AsyncSession):
    """Test run_all_scrapes with successful product extraction."""
    from src.app import database as db
    from src.app.scraper import run_all_scrapes
    
    # Create a test target
    target = db.ScrapeTarget(
        name="Success Store",
        base_url="http://success.com",
        name_selector="h1",
        price_selector=".price",
        url_selector="a"
    )
    await db.create_scrape_target(db_session, target)
    
    mock_html = """
    <html>
        <h1>Product A</h1>
        <span class="price">$99.99</span>
        <a href="/product-a">Link</a>
    </html>
    """
    
    with patch('src.app.scraper.ScraperService.fetch_html', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_html
        
        await run_all_scrapes(db_session)
        
        # Verify products were created
        products = await db.search_products_by_name(db_session, "Product A")
        assert len(products) >= 1
        
        # Verify log was created
        logs = await db.get_latest_scrape_logs(db_session, limit=1)
        assert len(logs) > 0
        assert logs[0].status == "success"
        assert logs[0].products_found >= 1


async def test_run_all_scrapes_with_html_fetch_failure(db_session: AsyncSession):
    """Test run_all_scrapes when HTML fetch fails."""
    from src.app import database as db
    from src.app.scraper import run_all_scrapes
    
    target = db.ScrapeTarget(
        name="Fail Store",
        base_url="http://fail.com",
        name_selector="h1",
        price_selector=".price",
        url_selector="a"
    )
    await db.create_scrape_target(db_session, target)
    
    with patch('src.app.scraper.ScraperService.fetch_html', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = None  # Simulate fetch failure
        
        await run_all_scrapes(db_session)
        
        # Verify failure log was created
        logs = await db.get_latest_scrape_logs(db_session, limit=10)
        fail_logs = [l for l in logs if l.target_name == "Fail Store"]
        assert len(fail_logs) > 0
        assert fail_logs[0].status == "failed"
        assert "Failed to fetch HTML" in fail_logs[0].error_message


async def test_run_all_scrapes_with_no_products_found(db_session: AsyncSession):
    """Test run_all_scrapes when HTML is fetched but no products found."""
    from src.app import database as db
    from src.app.scraper import run_all_scrapes
    
    target = db.ScrapeTarget(
        name="Empty Store",
        base_url="http://empty.com",
        name_selector="h1.product",
        price_selector=".price",
        url_selector="a.product-link"
    )
    await db.create_scrape_target(db_session, target)
    
    mock_html = "<html><body><h1>No products here</h1></body></html>"
    
    with patch('src.app.scraper.ScraperService.fetch_html', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_html
        
        await run_all_scrapes(db_session)
        
        # Verify success log with 0 products
        logs = await db.get_latest_scrape_logs(db_session, limit=10)
        empty_logs = [l for l in logs if l.target_name == "Empty Store"]
        assert len(empty_logs) > 0
        assert empty_logs[0].status == "success"
        assert empty_logs[0].products_found == 0


async def test_run_all_scrapes_with_upsert_error(db_session: AsyncSession):
    """Test run_all_scrapes continues when product upsert fails."""
    from src.app import database as db
    from src.app.scraper import run_all_scrapes
    
    target = db.ScrapeTarget(
        name="Error Store",
        base_url="http://error.com",
        name_selector="h1",
        price_selector=".price",
        url_selector="a"
    )
    await db.create_scrape_target(db_session, target)
    
    mock_html = """
    <html>
        <h1>Product B</h1>
        <span class="price">$50.00</span>
        <a href="/product-b">Link</a>
    </html>
    """
    
    with patch('src.app.scraper.ScraperService.fetch_html', new_callable=AsyncMock) as mock_fetch:
        with patch('src.app.database.upsert_product', new_callable=AsyncMock) as mock_upsert:
            mock_fetch.return_value = mock_html
            mock_upsert.side_effect = Exception("Database error")
            
            # Should not raise exception, should handle gracefully
            await run_all_scrapes(db_session)
            
            # Verify log was still created
            logs = await db.get_latest_scrape_logs(db_session, limit=10)
            error_logs = [l for l in logs if l.target_name == "Error Store"]
            assert len(error_logs) > 0
            # Log should show success (products were found, even if upsert failed)
            assert error_logs[0].status == "success"

