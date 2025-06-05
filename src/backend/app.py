"""
Main Starlette application for AdventureGPT.

This module contains the main application setup, middleware configuration,
and route registration.
"""

import json
import logging
from typing import Any, Dict

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from .api.game import app as game_app
from .api.routes import routes
from .db import close_db, init_db
from .middleware import JSONLoggingMiddleware
from .redis import close_redis, init_redis

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler()],
)


async def startup() -> None:
    """Initialize services on startup."""
    await init_db()
    await init_redis()


async def shutdown() -> None:
    """Clean up services on shutdown."""
    await close_db()
    await close_redis()


# Create the Starlette application
app = Starlette(
    debug=True,
    routes=[Mount("/api", app=game_app)],
    middleware=[
        Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"]),
        Middleware(JSONLoggingMiddleware),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown],
)
