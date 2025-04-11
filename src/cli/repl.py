import os
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style


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

    def _process_command(self, command: str) -> None:
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

        # TODO: Implement actual game command processing
        print(f"Command received: {command}")

    def _show_help(self):
        """Display help information"""
        help_text = """
Available Commands:
    look        - Look around the current location
    go [dir]    - Move in a direction (north, south, east, west)
    take [item] - Pick up an item
    drop [item] - Drop an item
    inventory   - Show your inventory
    use [item]  - Use an item
    examine [item] - Examine an item in detail
    help        - Show this help message
    quit        - Exit the game
    save        - Save your progress
    load        - Load a saved game
        """
        print(help_text)

    def run(self):
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
                self._process_command(user_input)

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit the game.")
            except EOFError:
                self.running = False
                print("\nGoodbye! Thanks for playing Colossal Adventure!")


def start_repl():
    """Start the game REPL"""
    repl = GameREPL()
    repl.run()


if __name__ == "__main__":
    start_repl()
