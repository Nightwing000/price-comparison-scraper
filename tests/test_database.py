"""
Tests for database CRUD operations.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.app import database as db

pytestmark = pytest.mark.asyncio


async def test_create_scrape_target(db_session: AsyncSession):
    """Test creating a scrape target."""
    target = db.ScrapeTarget(
        name="Amazon",
        base_url="http://amazon.com",
        name_selector=".product-name",
        price_selector=".price",
        url_selector=".product-link"
    )
    
    created = await db.create_scrape_target(db_session, target)
    assert created.id is not None
    assert created.name == "Amazon"


async def test_get_all_scrape_targets(db_session: AsyncSession):
    """Test retrieving all scrape targets."""
    # Create multiple targets
    target1 = db.ScrapeTarget(
        name="Store1",
        base_url="http://store1.com",
        name_selector="h1",
        price_selector="span",
        url_selector="a"
    )
    target2 = db.ScrapeTarget(
        name="Store2",
        base_url="http://store2.com",
        name_selector="h2",
        price_selector="div",
        url_selector="a"
    )
    
    await db.create_scrape_target(db_session, target1)
    await db.create_scrape_target(db_session, target2)
    
    targets = await db.get_all_scrape_targets(db_session)
    assert len(targets) >= 2
    names = [t.name for t in targets]
    assert "Store1" in names
    assert "Store2" in names


async def test_upsert_and_search_products(db_session: AsyncSession):
    """Test upserting products and then searching for them."""
    # Upsert products
    product_data1 = {
        "name": "Test Phone A",
        "price": 599.99,
        "url": "http://store.com/phone-a",
        "source_site": "Store"
    }
    product_data2 = {
        "name": "Test Phone B",
        "price": 699.99,
        "url": "http://store.com/phone-b",
        "source_site": "Store"
    }
    
    await db.upsert_product(db_session, product_data1)
    await db.upsert_product(db_session, product_data2)
    
    # Search for products
    results = await db.search_products_by_name(db_session, "Test Phone")
    assert len(results) >= 2
    
    # Update existing product
    product_data1["price"] = 549.99
    await db.upsert_product(db_session, product_data1)
    
    # Verify update
    results = await db.search_products_by_name(db_session, "Test Phone A")
    assert len(results) >= 1
    assert results[0].price == 549.99


async def test_logs_operations(db_session: AsyncSession):
    """Test creating and retrieving logs."""
    # Create logs
    log1 = db.ScrapeLog(
        target_name="Store X",
        status="success",
        products_found=10
    )
    log2 = db.ScrapeLog(
        target_name="Store Y",
        status="failed",
        error_message="Network error"
    )
    
    await db.create_scrape_log(db_session, log1)
    await db.create_scrape_log(db_session, log2)
    
    # Get recent logs
    logs = await db.get_latest_scrape_logs(db_session, limit=5)
    assert len(logs) >= 2
    
    # Verify log details
    log_names = [l.target_name for l in logs]
    assert "Store X" in log_names or "Store Y" in log_names

