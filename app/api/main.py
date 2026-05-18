import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.router import api_router
from app.core.logging_config import setup_logging
# Explicitly import models to ensure they are registered with Base.metadata before create_all
from app.api.task_model import Task
from app.api.session import get_engine, Base

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application lifespan events.
    Attempts to initialize database tables without blocking startup if the DB is unavailable.
    """
    try:
        Base.metadata.create_all(bind=get_engine())
        logger.info("Database tables verified.")
    except Exception as e:
        logger.error(f"Database initialization failed on startup: {e}. API starting in degraded mode.")
    yield

setup_logging()

app = FastAPI(
    title="NLP RAG Pipeline",
    lifespan=lifespan
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {
        "message": "NLP RAG API Running"
    }