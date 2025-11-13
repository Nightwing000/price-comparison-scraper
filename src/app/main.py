"""
Main FastAPI application file.
Sets up the app, routers, and background scheduler.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from .api import api_router
from .scheduler import scheduler, start_scheduler, shutdown_scheduler
from .database import engine, Base
from .core import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan manager for the FastAPI app.
    Handles startup and shutdown events.
    """
    print("Application startup...")
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start the scheduler
    start_scheduler()
    print("Scheduler started.")
    
    yield
    
    # Shutdown the scheduler
    print("Application shutdown...")
    await shutdown_scheduler()
    print("Scheduler shut down.")

app = FastAPI(
    title="Price Comparison Scraper API",
    version="1.0",
    lifespan=lifespan
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint for health check.
    """
    return {"message": "Welcome to the Price Comparison API!"}

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation Error", "errors": exc.errors()},
    )

if __name__ == "__main__":
    # This is for running the app directly (e.g., for debugging)
    uvicorn.run("src.app.main:app", host="127.0.0.1", port=8000, reload=True)
