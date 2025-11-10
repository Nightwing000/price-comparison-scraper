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
):pass
    