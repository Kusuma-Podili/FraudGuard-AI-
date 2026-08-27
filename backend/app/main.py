"""FraudGuard AI: FastAPI Application Entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from backend.app.core.config import settings
from backend.app.core.logging import setup_logging, get_logger
from backend.app.core.middleware import (
    CorrelationIdMiddleware,
    RequestTimingMiddleware,
    fraudguard_exception_handler
)
from backend.app.core.exceptions import FraudGuardException
from backend.app.db.session import init_database, AsyncSessionLocal
from backend.app.db.init_db import seed_initial_data
from backend.app.api.v1.router import api_router

# Initialize structured logging
setup_logging()
logger = get_logger("fraudguard.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan management."""
    logger.info("Initializing FraudGuard AI platform...")
    # Initialize DB schemas and seed initial demo data
    try:
        await init_database()
        async with AsyncSessionLocal() as session:
            await seed_initial_data(session)
        logger.info("Database schemas and seed data ready.")
    except Exception as e:
        logger.warning(f"Database initialization note: {e}")

    yield

    logger.info("Shutting down FraudGuard AI...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middlewares
app.add_middleware(RequestTimingMiddleware)
app.add_middleware(CorrelationIdMiddleware)

# Exception Handlers
app.add_exception_handler(FraudGuardException, fraudguard_exception_handler)

# Include API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirect root traffic to OpenAPI interactive documentation."""
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")
