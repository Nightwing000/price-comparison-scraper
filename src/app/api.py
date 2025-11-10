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