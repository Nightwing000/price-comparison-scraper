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