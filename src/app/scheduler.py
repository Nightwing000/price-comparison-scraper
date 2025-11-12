"""
APScheduler setup for running background scraping jobs.
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from .core import settings
from .database import AsyncSessionFactory
from .scraper import run_all_scrapes

# Set up the job store to use the same database as the app
# Note: APScheduler's SQLAlchemyJobStore is synchronous,
# so we use a synchronous URL for it.
sync_db_url = settings.DATABASE_URL.replace(
    "sqlite+aiosqlite", "sqlite"
).replace(
    "postgresql+asyncpg", "postgresql"
)

jobstores = {
    'default': SQLAlchemyJobStore(url=sync_db_url)
}

scheduler = AsyncIOScheduler(jobstores=jobstores)

async def async_scrape_job():
    """
    Wrapper function to run the async scrape job.
    Creates its own DB session.
    """
    print("Scheduler job: Running all scrapes...")
    async with AsyncSessionFactory() as session:
        try:
            await run_all_scrapes(session)
            print("Scheduler job: Scrapes completed.")
        except Exception as e:
            print(f"Scheduler job: FAILED with error: {e}")

def start_scheduler():
    """
    Adds the job to the scheduler and starts it.
    """
    try:
        # Add the job
        scheduler.add_job(
            async_scrape_job,
            'interval',
            minutes=settings.SCHEDULER_INTERVAL_MINUTES,
            id='run_all_scrapes_job',
            replace_existing=True
        )
        # Start the scheduler
        if not scheduler.running:
            scheduler.start()
    except Exception as e:
        print(f"Error starting scheduler: {e}")