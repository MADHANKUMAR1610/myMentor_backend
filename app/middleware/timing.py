"""Request timing middleware."""

import time

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)


class ProcessTimeMiddleware(
    BaseHTTPMiddleware,
):
    """Measure request processing time."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        """Process request."""

        start_time = time.perf_counter()

        response = await call_next(
            request,
        )

        process_time = (
            time.perf_counter()
            - start_time
        )

        response.headers[
            "X-Process-Time"
        ] = f"{process_time:.6f}"

        return response