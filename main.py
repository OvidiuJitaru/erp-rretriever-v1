import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings
from app.database.mongo import connect_to_mongo, close_mongo_connection
from app.database.chroma import connect_to_chromaDB
from app.services.embedding_service import initialize_embedding_service
from app.retriever.RRetriever import initialize_rag_retriever
from app.routers.search_router import router as search_router
from app.models.api_models import ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting RAG Retriever service...")

    try:
        # Initialize services in order
        logger.info("1. Connecting to MongoDB...")
        await connect_to_mongo()

        logger.info("2. Connecting to ChromaDB...")
        await connect_to_chromaDB()

        logger.info("3. Initializing embedding service...")
        await initialize_embedding_service()

        logger.info("4. Initializing RAG retriever...")
        await initialize_rag_retriever()

        logger.info("✅ All services initialized successfully!")

    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")
        raise e

    # App is running
    yield

    # Shutdown
    logger.info("🛑 Shutting down RAG Retriever service...")
    try:
        await close_mongo_connection()
        logger.info("✅ MongoDB connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing MongoDB connection: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    RAG Retriever API for SQL Assistant

    This microservice provides context retrieval for a RAG-based SQL assistant.
    It combines vector search with hybrid filtering to find relevant SQL logic 
    examples and database schema information.

    ## Features
    - **Logic-driven retrieval**: Finds similar SQL patterns and includes related schemas
    - **Schema-only fallback**: When no relevant logic found, retrieves matching schemas
    - **Domain-specific configuration**: Different thresholds and limits per domain
    - **Hybrid search**: Combines vector similarity with keyword boosting
    - **Auto-join inclusion**: Automatically includes related tables based on foreign keys
    - **Dual embedding models**: Specialized models for SQL logic vs schema descriptions

    ## Domains
    Supported domains: ordini, magazzino, clienti, contabilita
    """,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_router)


@app.get("/")
async def root():
    """Root endpoint with basic service information"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/metrics")
async def get_metrics():
    """Basic metrics endpoint"""
    try:
        from app.database.mongo import get_mongo_client
        from app.database.chroma import get_chroma_client
        from app.services.embedding_service import get_embedding_service

        # Get basic metrics
        mongo_client = get_mongo_client()

        # Database stats
        db_stats = await mongo_client.get_database_stats()

        # Collection stats
        schema_stats = await mongo_client.get_collection_stats(settings.mongo_table_schema_collection)
        logic_stats = await mongo_client.get_collection_stats(settings.mongo_logic_collection)

        # Model info
        embedding_service = get_embedding_service()
        model_info = embedding_service.get_model_info()

        return {
            "timestamp": datetime.now().isoformat(),
            "database": {
                "mongodb": {
                    "database_size_mb": round(db_stats.get("dataSize", 0) / (1024 * 1024), 2),
                    "collections": {
                        "schemas": {
                            "count": schema_stats.get("count", 0),
                            "size_mb": round(schema_stats.get("size", 0) / (1024 * 1024), 2)
                        },
                        "logics": {
                            "count": logic_stats.get("count", 0),
                            "size_mb": round(logic_stats.get("size", 0) / (1024 * 1024), 2)
                        }
                    }
                }
            },
            "models": {
                "embedding_model": model_info
            },
            "configuration": {
                "domains": list(settings.get_domain_configs().keys()),
                "debug_mode": settings.debug
            }
        }

    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving metrics: {str(e)}"
        )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception in {request.url}: {exc}")

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else "An unexpected error occurred",
            timestamp=datetime.now()
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )