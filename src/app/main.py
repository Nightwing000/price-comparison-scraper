"""
Main FastAPI application file.
Sets up the app, routers, and background scheduler.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn

from .database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    pass
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