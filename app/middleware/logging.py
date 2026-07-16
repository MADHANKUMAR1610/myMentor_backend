"""Request logging middleware."""

import logging
import time

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)

logger = logging.getLogger(__name__)


class LoggingMiddleware(
    BaseHTTPMiddleware,
):
    """Log incoming requests and responses."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        """Process the request."""

        start_time = time.perf_counter()

        logger.info(
            "Started %s %s",
            request.method,
            request.url.path,
        )

        response = await call_next(
            request,
        )

        duration = (
            time.perf_counter()
            - start_time
        ) * 1000

        logger.info(
            "Completed %s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )

        return response