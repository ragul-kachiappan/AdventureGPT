"""
Configuration module for AdventureGPT.

This module handles environment variables and application settings.
"""

import os
from typing import Optional

from pydantic import BaseSettings, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "adventuregpt"
    POSTGRES_PORT: str = "5432"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def DATABASE_URL(self) -> PostgresDsn:
        """Get the database URL."""
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}",
        )

    @property
    def REDIS_URL(self) -> RedisDsn:
        """Get the Redis URL."""
        return RedisDsn.build(
            scheme="redis",
            host=self.REDIS_HOST,
            port=str(self.REDIS_PORT),
            path=f"/{self.REDIS_DB}",
        )

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Export commonly used settings
DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL
