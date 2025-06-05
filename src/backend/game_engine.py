import json
from typing import Dict, List, Optional, Tuple

from .models import Direction, GameState, Item, PlayerState, Room
from .redis import get_redis_client


class GameEngine:
    def __init__(self):
        self.redis = get_redis_client()
        self._initialize_game()

    def _initialize_game(self):
        """Initialize the game with basic rooms and items if not already initialized."""
        if not self.redis.exists("game_state"):
            initial_state = GameState(
                player=PlayerState(current_room="entrance"),
                rooms=self._create_initial_rooms(),
                items=self._create_initial_items(),
                game_started=True,
                game_over=False,
            )
            self._save_game_state(initial_state)

    def _create_initial_rooms(self) -> Dict[str, Room]:
        """Create the initial set of rooms for the game."""
        return {
            "entrance": Room(
                id="entrance",
                name="Outside Cave Entrance",
                description="You are standing at the entrance of a cave. The entrance is large and dark.",
                exits={Direction.NORTH: "main_cave", Direction.SOUTH: "forest"},
                items=["lamp"],
            ),
            "main_cave": Room(
                id="main_cave",
                name="Main Cave",
                description="You are in a large cave. The walls are damp and the air is cool.",
                exits={
                    Direction.SOUTH: "entrance",
                    Direction.EAST: "east_passage",
                    Direction.WEST: "west_passage",
                },
            ),
            # Add more rooms as needed
        }

    def _create_initial_items(self) -> Dict[str, Item]:
        """Create the initial set of items for the game."""
        return {
            "lamp": Item(
                name="lamp",
                description="A brass lamp that provides light in dark places.",
                is_portable=True,
                is_visible=True,
                is_takeable=True,
            ),
            # Add more items as needed
        }

    def _save_game_state(self, state: GameState):
        """Save the current game state to Redis."""
        self.redis.set("game_state", state.model_dump_json())

    def _load_game_state(self) -> GameState:
        """Load the current game state from Redis."""
        state_json = self.redis.get("game_state")
        if not state_json:
            raise ValueError("No game state found in Redis")
        return GameState.model_validate_json(state_json)

    def get_room_description(self, room_id: str) -> str:
        """Get the description of a room."""
        state = self._load_game_state()
        room = state.rooms.get(room_id)
        if not room:
            return "You can't see anything."
        return room.description

    def move_player(self, direction: Direction) -> Tuple[bool, str]:
        """Move the player in the specified direction."""
        state = self._load_game_state()
        current_room = state.rooms[state.player.current_room]

        if direction not in current_room.exits:
            return False, f"You can't go {direction} from here."

        new_room_id = current_room.exits[direction]
        if new_room_id not in state.rooms:
            return False, "That way is blocked."

        state.player.current_room = new_room_id
        if new_room_id not in state.player.visited_rooms:
            state.player.visited_rooms.append(new_room_id)

        self._save_game_state(state)
        return True, f"You move {direction} to {state.rooms[new_room_id].name}."

    def take_item(self, item_name: str) -> Tuple[bool, str]:
        """Take an item from the current room."""
        state = self._load_game_state()
        current_room = state.rooms[state.player.current_room]

        if item_name not in current_room.items:
            return False, f"There is no {item_name} here."

        item = state.items[item_name]
        if not item.is_takeable:
            return False, f"You can't take the {item_name}."

        current_room.items.remove(item_name)
        state.player.inventory.append(item_name)
        self._save_game_state(state)
        return True, f"You take the {item_name}."

    def drop_item(self, item_name: str) -> Tuple[bool, str]:
        """Drop an item in the current room."""
        state = self._load_game_state()

        if item_name not in state.player.inventory:
            return False, f"You don't have the {item_name}."

        state.player.inventory.remove(item_name)
        state.rooms[state.player.current_room].items.append(item_name)
        self._save_game_state(state)
        return True, f"You drop the {item_name}."

    def get_inventory(self) -> List[str]:
        """Get the player's inventory."""
        state = self._load_game_state()
        return state.player.inventory

    def get_current_room(self) -> Room:
        """Get the player's current room."""
        state = self._load_game_state()
        return state.rooms[state.player.current_room]

    def toggle_lamp(self) -> Tuple[bool, str]:
        """Toggle the lamp on/off."""
        state = self._load_game_state()
        if "lamp" not in state.player.inventory:
            return False, "You don't have a lamp."

        state.player.is_lamp_on = not state.player.is_lamp_on
        self._save_game_state(state)
        status = "on" if state.player.is_lamp_on else "off"
        return True, f"You turn the lamp {status}."

    def get_visible_items(self) -> List[str]:
        """Get items visible in the current room."""
        state = self._load_game_state()
        current_room = state.rooms[state.player.current_room]
        return [
            item_name
            for item_name in current_room.items
            if state.items[item_name].is_visible
        ]

    def reset_game(self):
        """Reset the game to its initial state."""
        self._initialize_game()
