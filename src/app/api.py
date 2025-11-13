"""
All API endpoints for the application.
Includes security dependencies for API key authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, HttpUrl, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from . import database as db
from . import scraper
from .core import settings

api_router = APIRouter()

# --- API Key Security ---
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

async def get_client_api_key(key: str = Security(api_key_header)):
    """Dependency to validate the client API key."""
    if key == settings.CLIENT_API_KEY:
        return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing client API key"
    )

async def get_admin_api_key(key: str = Security(api_key_header)):
    """Dependency to validate the admin API key."""
    if key == settings.ADMIN_API_KEY:
        return key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing admin API key"
    )

# --- Pydantic Schemas (for API request/response) ---

# Product Schemas
class ProductBase(BaseModel):
    name: str
    price: float
    url: str
    source_site: str

class ProductPublic(ProductBase):
    id: int
    scraped_at: str # Use string for JSON compatibility

    model_config = ConfigDict(from_attributes=True)

# ScrapeTarget Schemas
class ScrapeTargetCreate(BaseModel):
    name: str
    base_url: str
    name_selector: str
    price_selector: str
    url_selector: str

class ScrapeTargetPublic(ScrapeTargetCreate):
    id: int
    created_at: str

    class Config:
        from_attributes = True
    model_config = ConfigDict(from_attributes=True)

# ScrapeLog Schemas
class ScrapeLogPublic(BaseModel):
    id: int
    target_name: str
    status: str
    products_found: int
    error_message: str | None
    created_at: str

    model_config = ConfigDict(from_attributes=True)


# --- Client API Endpoints ---

@api_router.get(
    "/search",
    response_model=List[ProductPublic],
    dependencies=[Depends(get_client_api_key)]
)
async def search_products(q: str, db_session: AsyncSession = Depends(db.get_db)):
    """
    Search for products by name.
    Requires a valid client API key.
    """
    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' is required.")
    
    products = await db.search_products_by_name(db_session, q)
    
    # Convert datetime objects to ISO 8601 strings for JSON response
    return [
        ProductPublic(
            id=product.id,
            name=product.name,
            price=product.price,
            url=product.url,
            source_site=product.source_site,
            scraped_at=product.scraped_at.isoformat()
        ) for product in products
    ]

# --- Admin API Endpoints ---

@api_router.post(
    "/admin/target",
    response_model=ScrapeTargetPublic,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_admin_api_key)]
)
async def add_scrape_target(
    target: ScrapeTargetCreate, 
    db_session: AsyncSession = Depends(db.get_db)
    
):
    """
    Add a new website target for scraping.
    Requires a valid admin API key.
    """
    db_target = db.ScrapeTarget(**target.model_dump())
    new_target = await db.create_scrape_target(db_session, db_target)
    
    return ScrapeTargetPublic(
        id=new_target.id,
        name=new_target.name,
        base_url=new_target.base_url,
        name_selector=new_target.name_selector,
        price_selector=new_target.price_selector,
        url_selector=new_target.url_selector,
        created_at=new_target.created_at.isoformat()
    )

@api_router.get(
    "/admin/logs",
    response_model=List[ScrapeLogPublic],
    dependencies=[Depends(get_admin_api_key)]
)
async def get_scrape_logs(db_session: AsyncSession = Depends(db.get_db)):
    """
    Get the 10 most recent scrape logs.
    Requires a valid admin API key.
    """
    
    logs = await db.get_latest_scrape_logs(db_session, limit=10)
    
    return [
        ScrapeLogPublic(
            id=log.id,
            target_name=log.target_name,
            status=log.status,
            products_found=log.products_found,
            error_message=log.error_message,
            created_at=log.created_at.isoformat()
        ) for log in logs
    ]

@api_router.post(
    "/admin/trigger-scrape",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(get_admin_api_key)]
)
async def trigger_manual_scrape(db_session: AsyncSession = Depends(db.get_db)):
    """
    Manually trigger the scraping job for all targets.
    This runs in the background.
    Requires a valid admin API key.
    """
    try:
        await scraper.run_all_scrapes(db_session)
        return {"message": "Scraping job triggered successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger scrape: {e}")
