"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import trades
from app.core.config import settings
from app.core.logging_config import get_logger, setup_logging
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.repositories.database import init_db

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    logger.info("Starting Trade Store API...")
    init_db()
    logger.info("Database initialized")

    # Start background scheduler for expiry updates
    start_scheduler()

    yield

    # Shutdown
    logger.info("Shutting down Trade Store API...")
    shutdown_scheduler()


# Create FastAPI application
app = FastAPI(
    title="Trade Store API",
    description="API for managing trades with validation and business rules",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication Middleware (currently disabled)
# Uncomment to enable JWT authentication and authorization
# from app.middleware import AuthMiddleware
# app.add_middleware(
#     AuthMiddleware,
#     secret_key=settings.secret_key,  # Add to settings
#     algorithm="HS256"
# )

# Include routers
app.include_router(trades.router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        dict[str, str]: Health status
    """
    return {"status": "healthy"}


@app.get("/health/db")
def database_health() -> dict:
    """
    Database health check with connection pool status.

    Returns:
        dict: Database status and pool statistics
    """
    from app.repositories.database import get_pool_status

    try:
        pool_status = get_pool_status()
        return {"status": "healthy", "database": "connected", "pool": pool_status}
    except Exception as e:
        return {"status": "unhealthy", "database": "error", "error": str(e)}


@app.get("/")
def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        dict[str, str]: Welcome message
    """
    return {"message": "Trade Store API", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
