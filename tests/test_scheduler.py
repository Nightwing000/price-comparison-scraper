"""
Tests for scheduler functionality.
"""

import pytest


# Note: Scheduler tests are minimal since scheduler functionality
# is tested via integration tests and manual testing.
# Full scheduler testing would require more complex mocking of APScheduler.

def test_scheduler_module_imports():
    """Test that scheduler module can be imported and has required functions."""
    from src.app.scheduler import start_scheduler, shutdown_scheduler, async_scrape_job, scheduler
    
    assert callable(start_scheduler)
    assert callable(shutdown_scheduler)
    assert callable(async_scrape_job)
    assert scheduler is not None


