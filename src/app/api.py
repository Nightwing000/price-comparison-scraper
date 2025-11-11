from typing import List
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from . import database as db
from .core import settings

api_router = APIRouter()

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
    