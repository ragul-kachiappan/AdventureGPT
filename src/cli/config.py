import os
from typing import Optional

# Default backend URL - can be overridden by environment variable
DEFAULT_BACKEND_URL = "http://localhost:8000/api"


def get_backend_url() -> str:
    """Get the backend URL from environment variable or use default."""
    return os.getenv("ADVENTURE_BACKEND_URL", DEFAULT_BACKEND_URL)


# API endpoints
def get_api_endpoint(endpoint: str) -> str:
    """Get the full API endpoint URL."""
    return f"{get_backend_url()}/game/{endpoint}"
