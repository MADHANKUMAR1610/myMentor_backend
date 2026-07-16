"""Request ID middleware."""

import uuid

from fastapi import Request
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)


class RequestIDMiddleware(
    BaseHTTPMiddleware,
):
    """Attach a unique request ID."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):
        """Process the request."""

        request_id = str(
            uuid.uuid4()
        )

        request.state.request_id = request_id

        response = await call_next(
            request,
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        return response