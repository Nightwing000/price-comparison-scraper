from datetime import datetime
from typing import AsyncGenerator, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, DateTime, ForeignKey, Integer, func, select
from .core import settings

# --- Database Engine Setup ---
engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get an async database session.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()