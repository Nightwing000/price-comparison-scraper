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

class ScrapeLog(Base):
    """
    Model for logging scrape job executions.
    """
    __tablename__ = "scrape_logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    target_name: Mapped[str] = mapped_column(String(100), index=True)
    status: Mapped[str] = mapped_column(String(50)) # "success" or "failed"
    products_found: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

#CRUD Operations
async def create_scrape_target(db: AsyncSession, target: ScrapeTarget) -> ScrapeTarget:
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return target

async def get_all_scrape_targets(db: AsyncSession) -> List[ScrapeTarget]:
    result = await db.execute(select(ScrapeTarget))
    return list(result.scalars().all())

async def upsert_product(db: AsyncSession, product_data: dict):
    """
    Create a new product or update it if it already exists (based on URL).
    """
    stmt = select(Product).where(Product.url == product_data['url'])
    result = await db.execute(stmt)
    existing_product = result.scalars().first()

    if existing_product:
        # Update existing
        existing_product.name = product_data['name']
        existing_product.price = product_data['price']
        existing_product.scraped_at = func.now()

    else:
        # Create new
        new_product = Product(**product_data)
        db.add(new_product)
    
    await db.commit()

async def search_products_by_name(db: AsyncSession, query: str) -> List[Product]:
    """
    Search for products where the name contains the query string.
    """
    stmt = select(Product).where(Product.name.ilike(f"%{query}%"))
    result = await db.execute(stmt)
    return list(result.scalars().all())
async def search_products_by_name(db: AsyncSession, query: str) -> List[Product]:
    stmt = select(Product).where(Product.name.ilike(f"%{query}%"))
    result = await db.execute(stmt)
    return list(result.scalars().all())

async def create_scrape_log(db: AsyncSession, log: ScrapeLog) -> ScrapeLog:
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log

async def get_latest_scrape_logs(db: AsyncSession, limit: int = 10) -> List[ScrapeLog]:
    stmt = select(ScrapeLog).order_by(ScrapeLog.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())