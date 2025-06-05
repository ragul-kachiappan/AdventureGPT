"""
Redis module for AdventureGPT.

This module handles Redis connections and session management.
"""

import json
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis

from .config import REDIS_URL


class RedisClient:
    """Redis client wrapper for session management."""

    _client: Optional[Redis] = None

    @classmethod
    async def get_client(cls) -> Redis:
        """Get or create a Redis client instance."""
        if cls._client is None:
            cls._client = redis.from_url(
                str(REDIS_URL),
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._client

    @classmethod
    async def close(cls) -> None:
        """Close the Redis client connection."""
        if cls._client is not None:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def get_session(cls, session_id: str) -> Optional[dict]:
        """Get a session from Redis."""
        client = await cls.get_client()
        data = await client.get(f"session:{session_id}")
        return json.loads(data) if data else None

    @classmethod
    async def set_session(cls, session_id: str, data: dict, expire: int = 3600) -> None:
        """Set a session in Redis with expiration."""
        client = await cls.get_client()
        await client.set(
            f"session:{session_id}",
            json.dumps(data),
            ex=expire,
        )

    @classmethod
    async def delete_session(cls, session_id: str) -> None:
        """Delete a session from Redis."""
        client = await cls.get_client()
        await client.delete(f"session:{session_id}")


async def init_redis() -> None:
    """Initialize Redis connection."""
    await RedisClient.get_client()


async def close_redis() -> None:
    """Close Redis connection."""
    await RedisClient.close()
