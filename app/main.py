"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.core.handlers import register_exception_handlers
from app.core.logging import setup_logging
from app.database import (
    close_database,
    connect_database,
)
from app.middleware import LoggingMiddleware

from app.middleware import (
    LoggingMiddleware,
    ProcessTimeMiddleware,
    RequestIDMiddleware,
)
setup_logging()


@asynccontextmanager
async def lifespan(
    app: FastAPI,
) -> AsyncIterator[None]:
    """Manage application startup and shutdown."""

    await connect_database()

    yield

    await close_database()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""

    application = FastAPI(
        title=settings.APP_NAME,
        description="Backend API for Digipin Academy LMS",
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    register_exception_handlers(
        application,
    )

    application.add_middleware(
        CORSMiddleware,
       
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(
    RequestIDMiddleware,
)

    application.add_middleware(
    ProcessTimeMiddleware,
)

    application.add_middleware(
    LoggingMiddleware,
)
    application.include_router(
        api_router,
        prefix="/api",
    )

    return application


app = create_application()