"""
API handlers for AdventureGPT.

This module contains the request handlers for the game API.
"""

import json
from typing import Any, Dict

from starlette.requests import Request
from starlette.responses import JSONResponse

from ..redis import RedisClient


async def game_state(request: Request) -> JSONResponse:
    """Get the current game state."""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return JSONResponse(
            {"error": "Session ID required"},
            status_code=400,
        )

    session = await RedisClient.get_session(session_id)
    if not session:
        return JSONResponse(
            {"error": "Session not found"},
            status_code=404,
        )

    return JSONResponse(session)


async def execute_command(request: Request) -> JSONResponse:
    """Execute a game command."""
    session_id = request.headers.get("X-Session-ID")
    if not session_id:
        return JSONResponse(
            {"error": "Session ID required"},
            status_code=400,
        )

    try:
        body = await request.json()
        command = body.get("command")
        if not command:
            return JSONResponse(
                {"error": "Command required"},
                status_code=400,
            )

        # TODO: Implement command execution logic
        # This will be integrated with game_engine.py

        return JSONResponse(
            {
                "message": "Command executed successfully",
                "command": command,
            }
        )
    except json.JSONDecodeError:
        return JSONResponse(
            {"error": "Invalid JSON"},
            status_code=400,
        )
