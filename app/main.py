from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.meta import setup_logging

from app.routers.chatbot_router import chat_router

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


setup_logging(debug=settings.debug)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # connect to sqlserver
    ...
    yield
    # close sqlserver connection
    ...

app = FastAPI(
    title="Formula Agent API",
    description="SQL agentic assistant for ERP software",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/agent/api/v1")

# Health check
@app.get("/healthCheck")
async def health_check():
    """Health check endpoint"""
    try:
        from datetime import datetime, timezone

        utc_dt = datetime.now(timezone.utc)  # UTC time

        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"


    return {
        "status": db_status,
        "time_and_zone": utc_dt.isoformat() if utc_dt else None,
        "version": settings.app_version
    }