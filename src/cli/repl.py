import os
from pathlib import Path
from typing import Any, Dict, Tuple

import httpx
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from .config import get_api_endpoint


class GameREPL:
    """Interactive REPL for the Colossal Adventure game"""

    def __init__(self):
        # Create history directory if it doesn't exist
        history_dir = Path.home() / ".colossal_adventure"
        history_dir.mkdir(exist_ok=True)
        history_file = history_dir / "history.txt"

        # Initialize prompt session with history
        self.session = PromptSession(
            history=FileHistory(str(history_file)),
            auto_suggest=AutoSuggestFromHistory(),
            style=self._get_style(),
        )

        # Basic command completer
        self.commands = [
            "look",
            "go",
            "take",
            "drop",
            "inventory",
            "use",
            "examine",
            "help",
            "quit",
            "save",
            "load",
        ]
        self.completer = WordCompleter(self.commands, ignore_case=True)

        # Game state
        self.running = True
        self.client = httpx.AsyncClient()

    def _get_style(self):
        """Define the style for the prompt"""
        return Style.from_dict(
            {
                "prompt": "#FFD700 bold",  # Gold color for prompt
                "input": "#FFFFFF",  # White for input
                "completion-menu.completion": "bg:#282828 #FFFFFF",
                "completion-menu.completion.current": "bg:#3c3c3c #FFFFFF",
            }
        )

    def _get_prompt(self):
        """Get the formatted prompt"""
        return HTML("<prompt>▶ </prompt>")

    async def _get_game_state(self) -> Dict[str, Any]:
        """Get the current game state from the API."""
        response = await self.client.get(get_api_endpoint("state"))
        response.raise_for_status()
        return response.json()

    async def _move_player(self, direction: str) -> Tuple[bool, str]:
        """Move the player in a direction."""
        try:
            response = await self.client.post(
                get_api_endpoint("move"), json={"direction": direction}
            )
            response.raise_for_status()
            return True, response.json()["message"]
        except httpx.HTTPStatusError as e:
            return False, e.response.json()["error"]

    async def _take_item(self, item: str) -> Tuple[bool, str]:
        """Take an item from the current room."""
        try:
            response = await self.client.post(
                get_api_endpoint("take"), json={"item": item}
            )
            response.raise_for_status()
            return True, response.json()["message"]
        except httpx.HTTPStatusError as e:
            return False, e.response.json()["error"]

    async def _drop_item(self, item: str) -> Tuple[bool, str]:
        """Drop an item in the current room."""
        try:
            response = await self.client.post(
                get_api_endpoint("drop"), json={"item": item}
            )
            response.raise_for_status()
            return True, response.json()["message"]
        except httpx.HTTPStatusError as e:
            return False, e.response.json()["error"]

    async def _toggle_lamp(self) -> Tuple[bool, str]:
        """Toggle the lamp on/off."""
        try:
            response = await self.client.post(get_api_endpoint("lamp"))
            response.raise_for_status()
            return True, response.json()["message"]
        except httpx.HTTPStatusError as e:
            return False, e.response.json()["error"]

    async def _reset_game(self) -> Tuple[bool, str]:
        """Reset the game to its initial state."""
        try:
            response = await self.client.post(get_api_endpoint("reset"))
            response.raise_for_status()
            return True, response.json()["message"]
        except httpx.HTTPStatusError as e:
            return False, e.response.json()["error"]

    async def _process_command(self, command: str) -> None:
        """Process the user's command"""
        command = command.strip().lower()

        if not command:
            return

        if command == "quit":
            self.running = False
            print("Goodbye! Thanks for playing Colossal Adventure!")
            return

        if command == "help":
            self._show_help()
            return

        if command == "look":
            state = await self._get_game_state()
            current_room = state["current_room"]
            print(f"\n{current_room['name']}")
            print(f"{current_room['description']}")
            if current_room["items"]:
                print("\nItems here:")
                for item in current_room["items"]:
                    print(f"- {item}")
            if current_room["exits"]:
                print("\nExits:")
                for direction, room in current_room["exits"].items():
                    print(f"- {direction}")
            return

        if command.startswith("go "):
            direction = command[3:].strip()
            success, message = await self._move_player(direction)
            print(message)
            if success:
                await self._process_command("look")
            return

        if command.startswith("take "):
            item = command[5:].strip()
            success, message = await self._take_item(item)
            print(message)
            return

        if command.startswith("drop "):
            item = command[5:].strip()
            success, message = await self._drop_item(item)
            print(message)
            return

        if command == "inventory":
            state = await self._get_game_state()
            inventory = state["inventory"]
            if inventory:
                print("\nYour inventory:")
                for item in inventory:
                    print(f"- {item}")
            else:
                print("\nYour inventory is empty.")
            return

        if command.startswith("use "):
            item = command[4:].strip()
            if item == "lamp":
                success, message = await self._toggle_lamp()
                print(message)
            else:
                print(f"You can't use the {item}.")
            return

        print(f"I don't understand '{command}'. Type 'help' for a list of commands.")

    def _show_help(self):
        """Display help information"""
        help_text = """
Available Commands:
    look        - Look around the current location
    go [dir]    - Move in a direction (north, south, east, west)
    take [item] - Pick up an item
    drop [item] - Drop an item
    inventory   - Show your inventory
    use [item]  - Use an item (currently only 'lamp' is supported)
    help        - Show this help message
    quit        - Exit the game
        """
        print(help_text)

    async def run(self):
        """Run the REPL"""
        print("Welcome to Colossal Adventure!")
        print("Type 'help' for a list of commands or 'quit' to exit.")

        while self.running:
            try:
                # Get user input with completion
                user_input = self.session.prompt(
                    self._get_prompt(), completer=self.completer
                )

                # Process the command
                await self._process_command(user_input)

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit the game.")
            except EOFError:
                self.running = False
                print("\nGoodbye! Thanks for playing Colossal Adventure!")
            except httpx.RequestError as e:
                print(f"\nError connecting to game server: {str(e)}")
                print("Please make sure the game server is running.")
                self.running = False
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                self.running = False

        await self.client.aclose()


async def start_repl():
    """Start the game REPL"""
    repl = GameREPL()
    await repl.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_repl())
