from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ..game_engine import GameEngine
from ..models import Direction

game_engine = GameEngine()


async def get_game_state(request: Request):
    """Get the current game state."""
    try:
        current_room = game_engine.get_current_room()
        inventory = game_engine.get_inventory()
        visible_items = game_engine.get_visible_items()

        return JSONResponse(
            {
                "current_room": {
                    "name": current_room.name,
                    "description": current_room.description,
                    "exits": current_room.exits,
                    "items": visible_items,
                },
                "inventory": inventory,
            }
        )
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def move(request: Request):
    """Move the player in a direction."""
    try:
        data = await request.json()
        direction = Direction(data["direction"])
        success, message = game_engine.move_player(direction)

        if success:
            return JSONResponse({"message": message})
        else:
            return JSONResponse({"error": message}, status_code=400)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def take_item(request: Request):
    """Take an item from the current room."""
    try:
        data = await request.json()
        item_name = data["item"]
        success, message = game_engine.take_item(item_name)

        if success:
            return JSONResponse({"message": message})
        else:
            return JSONResponse({"error": message}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def drop_item(request: Request):
    """Drop an item in the current room."""
    try:
        data = await request.json()
        item_name = data["item"]
        success, message = game_engine.drop_item(item_name)

        if success:
            return JSONResponse({"message": message})
        else:
            return JSONResponse({"error": message}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def toggle_lamp(request: Request):
    """Toggle the lamp on/off."""
    try:
        success, message = game_engine.toggle_lamp()

        if success:
            return JSONResponse({"message": message})
        else:
            return JSONResponse({"error": message}, status_code=400)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def reset_game(request: Request):
    """Reset the game to its initial state."""
    try:
        game_engine.reset_game()
        return JSONResponse({"message": "Game has been reset"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


routes = [
    Route("/game/state", get_game_state, methods=["GET"]),
    Route("/game/move", move, methods=["POST"]),
    Route("/game/take", take_item, methods=["POST"]),
    Route("/game/drop", drop_item, methods=["POST"]),
    Route("/game/lamp", toggle_lamp, methods=["POST"]),
    Route("/game/reset", reset_game, methods=["POST"]),
]

app = Starlette(
    routes=routes,
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ],
)
