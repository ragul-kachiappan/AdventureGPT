"""
Middleware module for AdventureGPT.

This module contains custom middleware for the application,
including JSON logging middleware.
"""

import json
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp


class JSONLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for JSON-formatted request/response logging."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        logging.info(
            json.dumps(
                {
                    "type": "request",
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                }
            )
        )

        # Process request
        response = await call_next(request)

        # Log response
        logging.info(
            json.dumps(
                {
                    "type": "response",
                    "status_code": response.status_code,
                    "path": request.url.path,
                }
            )
        )

        return response
