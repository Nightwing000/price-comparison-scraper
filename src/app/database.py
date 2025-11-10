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

class ScrapeTarget(Base):
    """
    Model for a website target to be scraped.
    """
    __tablename__ = "scrape_targets"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    base_url: Mapped[str] = mapped_column(String(255))
    name_selector: Mapped[str] = mapped_column(String(255))
    price_selector: Mapped[str] = mapped_column(String(255))
    url_selector: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

class Product(Base):
    """
    Model for a scraped product.
    """
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    price: Mapped[float] = mapped_column(Float)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    source_site: Mapped[str] = mapped_column(String(100))
    scraped_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

#CRUD Operations
async def create_scrape_target(db: AsyncSession, target: ScrapeTarget) -> ScrapeTarget:
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target