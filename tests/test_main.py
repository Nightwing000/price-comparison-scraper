"""
Tests for main application functionality.
"""

import pytest
from httpx import AsyncClient, ASGITransport


def test_app_configuration():
    """Test that the app is properly configured."""
    from src.app.main import app
    
    assert "Price Comparison" in app.title
    assert app.version == "1.0"
    
    # Check that API router is included
    routes = [route.path for route in app.routes]
    assert any("/api/v1" in route for route in routes)


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    from src.app.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "API" in data["message"]


@pytest.mark.asyncio
async def test_validation_error_handler():
    """Test validation error handling."""
    from src.app.main import app
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try to add a target with invalid data (missing required fields)
        response = await client.post("/api/v1/admin/target", 
                                    json={"name": "Test"},  # Missing required fields
                                    headers={"x-api-key": "default_admin_secret"})
        
        # Should return 422 Unprocessable Entity
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data or "errors" in data

