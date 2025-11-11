import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from . import database as db
from .database import ScrapeTarget, ScrapeLog, Product

class ScraperService:
    """
    Handles the logic for scraping a single target.
    """
    def __init__(self, target: ScrapeTarget):
        self.target = target
        # Use httpx for async requests
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

    async def fetch_html(self) -> str | None:
        """Fetch the raw HTML from the target's base URL."""
        try:
            response = await self.client.get(self.target.base_url)
            response.raise_for_status() # Raise an exception for 4xx or 5xx
            return response.text
        except httpx.RequestError as e:
            print(f"Error fetching {self.target.base_url}: {e}")
            return None
        finally:
            await self.client.aclose()

    def _clean_price(self, price_str: str) -> float:
        """Utility to convert a price string to a float."""
        try:
            # Remove symbols like $, €, ,, etc.
            cleaned = "".join(c for c in price_str if c.isdigit() or c == '.')
            return float(cleaned)
        except ValueError:
            return 0.0
        
async def run_all_scrapes(db_session: AsyncSession):
    """
    The main job function.
    Fetches all targets, scrapes them, and logs the result.
    """
    targets = await db.get_all_scrape_targets(db_session)
    for target in targets:
        print(f"Scraping {target.name}...")
        service = ScraperService(target)
        html = await service.fetch_html()
        
        if not html:
            log = ScrapeLog(
                target_name=target.name,
                status="failed",
                error_message="Failed to fetch HTML."
            )
            await db.create_scrape_log(db_session, log)
            continue

        products = service.parse_html(html)
        
        if not products:
            log = ScrapeLog(
                target_name=target.name,
                status="success",
                products_found=0,
                error_message="HTML fetched but no products parsed."
            )
            await db.create_scrape_log(db_session, log)
            continue