"""
Tests for scheduler functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_async_scrape_job_success():
    """Test async_scrape_job function with successful execution."""
    from src.app.scheduler import async_scrape_job
    
    with patch('src.app.scheduler.run_all_scrapes', new_callable=AsyncMock) as mock_scrape:
        with patch('src.app.scheduler.AsyncSessionFactory') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_session
            
            await async_scrape_job()
            
            # Verify run_all_scrapes was called with the session
            mock_scrape.assert_called_once()


@pytest.mark.asyncio
async def test_async_scrape_job_with_exception():
    """Test async_scrape_job handles exceptions gracefully."""
    from src.app.scheduler import async_scrape_job
    
    with patch('src.app.scheduler.run_all_scrapes', new_callable=AsyncMock) as mock_scrape:
        with patch('src.app.scheduler.AsyncSessionFactory') as mock_session_factory:
            mock_session = AsyncMock()
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_session
            
            mock_scrape.side_effect = Exception("Test error")
            
            # Should not raise exception, should handle gracefully
            await async_scrape_job()


def test_scheduler_module_imports():
    """Test that scheduler module can be imported and has required functions."""
    from src.app.scheduler import start_scheduler, shutdown_scheduler, async_scrape_job, scheduler
    
    assert callable(start_scheduler)
    assert callable(shutdown_scheduler)
    assert callable(async_scrape_job)
    assert scheduler is not None


def test_start_scheduler_with_exception():
    """Test start_scheduler handles exceptions during startup."""
    from src.app.scheduler import scheduler
    
    with patch.object(scheduler, 'add_job') as mock_add_job:
        mock_add_job.side_effect = Exception("Job add failed")
        
        # Should not raise exception
        from src.app.scheduler import start_scheduler
        start_scheduler()


def test_scheduler_configuration():
    """Test scheduler is configured correctly."""
    from src.app.scheduler import scheduler, jobstores
    
    assert scheduler is not None
    assert 'default' in jobstores
    assert jobstores['default'] is not None


@pytest.mark.asyncio
async def test_shutdown_scheduler_when_not_running():
    """Test shutdown_scheduler when scheduler is not running."""
    from src.app.scheduler import shutdown_scheduler, scheduler
    
    # Ensure scheduler is not running
    if scheduler.running:
        scheduler.shutdown(wait=False)
    
    # Should handle gracefully
    await shutdown_scheduler()


