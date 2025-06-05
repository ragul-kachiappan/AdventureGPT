"""
Database module for AdventureGPT.

This module handles database connections and operations using
asyncpg and Tortoise ORM.
"""

import os
from typing import Optional

from tortoise import Tortoise
from tortoise.contrib.starlette import register_tortoise

from .config import DATABASE_URL


async def init_db() -> None:
    """Initialize database connections."""
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["src.backend.models"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    """Close database connections."""
    await Tortoise.close_connections()


def register_db(app) -> None:
    """Register Tortoise ORM with Starlette app."""
    register_tortoise(
        app,
        db_url=DATABASE_URL,
        modules={"models": ["src.backend.models"]},
        generate_schemas=True,
    )
