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
