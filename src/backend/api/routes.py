"""
API routes for AdventureGPT.

This module contains all the API routes for the game.
"""

from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from .handlers import execute_command, game_state

routes = [
    Route("/api/v1/game/state", game_state, methods=["GET"]),
    Route("/api/v1/game/command", execute_command, methods=["POST"]),
]
