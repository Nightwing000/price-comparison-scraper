from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from . import database as db
from .core import settings

api_router = APIRouter()

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

class ScrapeTargetCreate(BaseModel):
    """
    Schema for creating a new scrape target.
    Defines CSS selectors used by the scraper to extract data from a website.
    """
    name: str
    base_url: str
    name_selector: str
    price_selector: str
    url_selector: str

class ScrapeTargetPublic(ScrapeTargetCreate):
    """
    Response schema for returning scrape target details to the client.
    Extends ScrapeTargetCreate and includes database-generated fields.
    """
    id: int
    created_at: str

    class Config:
        from_attributes = True

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
        **new_target.__dict__,
        created_at=new_target.created_at.isoformat()
    )
    