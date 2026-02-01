from typing import Dict, List, Optional

from .models import Inventory, PlayerState, Room
from .storage import GameStorage


class GameEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.storage = GameStorage(db_path)
        self.state = PlayerState()
        # Initialize rooms data as Pydantic models (could be loaded from a file later)
        self.rooms: Dict[str, Room] = {
            "start": Room(
                description="You are standing at the end of a road before a small brick building.",
                exits={"north": "building", "in": "building"},
            ),
            "building": Room(
                description="You are inside a building, a well house for a large spring.",
                exits={"south": "start", "out": "start"},
            ),
        }

    def start_new_game(self):
        self.state = PlayerState()  # Reset state
        self.storage.new_game(self.state)
        return self._get_room_description()

    def resume_game(self):
        loaded_state = self.storage.load_player_state()
        if loaded_state:
            self.state = loaded_state
            return self._get_room_description()
        else:
            return self.start_new_game()

    def process_command(self, command: str) -> str:
        parts = command.lower().strip().split()
        if not parts:
            return "Please say something."

        verb = parts[0]

        if verb in ["quit", "exit"]:
            return "Goodbye!"

        if verb in ["look", "l"]:
            return self._get_room_description()

        if verb in ["go", "move", "walk"] and len(parts) > 1:
            direction = parts[1]
            return self._move(direction)

        # Simplified movement: just the direction
        if verb in ["north", "south", "east", "west", "up", "down", "in", "out"]:
            return self._move(verb)

        if verb == "inventory":
            if not self.state.inventory.items:
                return "You are not carrying anything."
            return f"You are carrying: {', '.join(self.state.inventory.items)}"

        return "I don't understand that command."

    def _move(self, direction: str) -> str:
        room_data = self.rooms.get(self.state.current_room)
        if not room_data:
            return "Error: You are in limbo."

        exits = room_data.exits
        if direction in exits:
            self.state.current_room = exits[direction]
            self.storage.save_player_state(self.state)
            return self._get_room_description()
        else:
            return "You can't go that way."

    def _get_room_description(self) -> str:
        room_data = self.rooms.get(self.state.current_room)
        if room_data:
            return room_data.description
        return "You are lost in the void."
