"""
System tests for end-to-end user flows.
These tests simulate a full workflow.
"""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

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
