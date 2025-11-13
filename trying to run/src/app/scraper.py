"""
Core web scraping service.
Fetches HTML from target sites, parses it, and saves data to the DB.
"""

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

    def parse_html(self, html: str) -> list[dict]:
        """Parse the HTML to find product data based on selectors."""
        soup = BeautifulSoup(html, 'html.parser')
        products_found = []

        # This logic assumes selectors point to containers.
        # A more robust parser would find all names, all prices, etc.
        # and try to align them.
        # For this project, we assume a simple structure
        # where we can find all elements of each type.
        
        try:
            names = [el.get_text(strip=True) for el in soup.select(self.target.name_selector)]
            prices = [self._clean_price(el.get_text(strip=True)) for el in soup.select(self.target.price_selector)]
            urls = [self._clean_url(el['href']) for el in soup.select(self.target.url_selector)]

            # Combine the lists, assuming they are in order
            for i in range(min(len(names), len(prices), len(urls))):
                products_found.append({
                    "name": names[i],
                    "price": prices[i],
                    "url": urls[i],
                    "source_site": self.target.name
                })
            
            return products_found
        
        except Exception as e:
            print(f"Error parsing HTML for {self.target.name}: {e}")
            return []

    def _clean_price(self, price_str: str) -> float:
        """Utility to convert a price string to a float."""
        try:
            # Remove symbols like $, €, ,, etc.
            cleaned = "".join(c for c in price_str if c.isdigit() or c == '.')
            return float(cleaned)
        except ValueError:
            return 0.0

    def _clean_url(self, url: str) -> str:
        """Utility to make a relative URL absolute."""
        if url.startswith('/'):
            # Create a base URL like "http://example.com"
            base = self.target.base_url.split('/')
            return f"{base[0]}//{base[2]}{url}"
        return url

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
            
        # If we found products, upsert them
        for product_data in products:
            try:
                await db.upsert_product(db_session, product_data)
            except Exception as e:
                print(f"Error upserting product {product_data.get('url')}: {e}")
        
        log = ScrapeLog(
            target_name=target.name,
            status="success",
            products_found=len(products)
        )
        await db.create_scrape_log(db_session, log)
        print(f"Successfully scraped {target.name}, found {len(products)} products.")
