import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from . import database as db
from .database import ScrapeTarget, ScrapeLog, Product

class ScraperService:
    pass