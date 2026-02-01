import asyncio
from typing import List

from textual.app import App, ComposeResult
from textual.suggester import Suggester
from textual.widgets import Footer, Header, Input, RichLog, Static

from adventuregpt.engine import GameEngine


class CommandSuggester(Suggester):
    """Simple autocomplete for game commands."""

    def __init__(self, commands: List[str]):
        super().__init__()
        self.commands = commands

    async def get_suggestion(self, value: str) -> str | None:
        if not value:
            return None
        for command in self.commands:
            if command.startswith(value):
                return command
        return None


class TypewriterLog(Static):
    """Widget to display text with a typewriter effect."""

    def update_text(self, text: str):
        self.update(text)


class AdventureApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    
    RichLog {
        height: 1fr;
        border: solid green;
        background: $surface;
        scrollbar-gutter: stable;
        overflow-y: scroll;
    }

    TypewriterLog {
        height: auto;
        min-height: 1;
        padding: 1;
        background: $surface;
        border-bottom: solid green;
    }
    
    Input {
        dock: bottom;
    }
    """

    BINDINGS = [("ctrl+c", "quit", "Quit"), ("ctrl+l", "clear_screen", "Clear Log")]

    COMMANDS = [
        "go north",
        "go south",
        "go east",
        "go west",
        "go in",
        "go out",
        "look",
        "inventory",
        "quit",
        "exit",
        "/help",
        "/learn",
    ]

    def __init__(self, engine: GameEngine, start_new: bool = False):
        super().__init__()
        self.engine = engine
        self.start_new = start_new
        self.current_text = ""
        self.is_typing = False
        self.typing_queue = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="game_log", markup=True)
        yield TypewriterLog(id="active_text")
        yield Input(
            placeholder="Type your command (TAB to autocomplete)...",
            id="command_input",
            suggester=CommandSuggester(self.COMMANDS),
        )
        yield Footer()

    def on_mount(self) -> None:
        if self.start_new:
            intro = self.engine.start_new_game()
        else:
            intro = self.engine.resume_game()

        self.log_message(intro)
        self.query_one(Input).focus()

    def log_message(self, message: str, animate: bool = True) -> None:
        if animate:
            self.animate_typewriter(message)
        else:
            log = self.query_one(RichLog)
            log.write(message)

    def animate_typewriter(self, message: str):
        # Cancel any existing typing? Or queue? For now, let's force finish previous
        # Ideally, we should move previous active text to log first.

        active_widget = self.query_one(TypewriterLog)
        history_log = self.query_one(RichLog)

        # If there is content in active widget, move it to history
        # We need to access the renderable or just rely on what we stored.
        # But for simplicity, let's assume we always move PREVIOUS message to history before starting NEW one.
        # However, at startup, there is no previous message.

        # Actually simplified flow:
        # 1. Write the *completed* string of any current animation to history immediately (skip animation).
        # 2. Clear active widget.
        # 3. Start new animation on active widget.

        # Since we don't track state perfectly here yet, let's just push what we INTENDED to write previously to history.
        # But wait, if I call log_message multiple times, they might overlap.
        # Let's enforce sequentiality or instant-finish.

        # Simplest approach for Phase 1:
        # Just write to history log directly IF it's a command echo.
        # Only animate descriptions/responses.

        self.typing_queue.append(message)
        if not self.is_typing:
            self.process_queue()

    def process_queue(self):
        if not self.typing_queue:
            self.is_typing = False
            return

        self.is_typing = True
        message = self.typing_queue.pop(0)
        self.current_type_message = message

        # Strip markup for typewriter effect, OR disable markup on the widget temporarily
        # Textual Static supports 'markup=False' in constructor or update?
        # A simpler way: The typewriter effect is complex with Rich Text tags.
        # For Phase 1, let's just show the full message if it contains markup tags,
        # or strip them if we really want to animate (but we lose colors).

        # Smart compromise: Detect if message has markup.
        if "[" in message and "]" in message:
            # Fast-forward for markup messages to avoid invalid XML-like slicing
            self.finalize_active_text()
            # We need to manually set current_type_message for finalize to work?
            # No, process_queue sets it.
            # Wait, finalize_active_text uses current_type_message.

            # But we want to show it in Active Text first?
            # Let's just update active text fully and wait a bit.
            self.get_widget_by_id("active_text").update(message)
            self.set_timer(1.0, self.finish_typing_markup_message)
            return

        self.current_type_message = message
        self.current_type_index = 0
        self.get_widget_by_id("active_text").update("")
        self.set_interval(0.02, self.type_next_char)

    def finish_typing_markup_message(self):
        self.finalize_active_text()
        self.process_queue()

    def type_next_char(self):
        # Determine how many chars to type (speed up for long text)
        chunk_size = 3 if len(self.current_type_message) > 100 else 1

        next_chunk = self.current_type_message[
            self.current_type_index : self.current_type_index + chunk_size
        ]
        self.current_type_index += len(next_chunk)

        active_widget = self.get_widget_by_id("active_text")

        current_display = self.current_type_message[: self.current_type_index]
        active_widget.update(current_display)

        if self.current_type_index >= len(self.current_type_message):
            # Done typing this message
            # Move it to history after a brief pause?
            # Or just keep it there until NEXT message comes?
            # User wants to read it.
            # So, keep it in "active_text".
            # BUT, if we have a queue, we need to move it to history.

            # Use call_later to finish up
            # Check if queue has more
            if self.typing_queue:
                self.finalize_active_text()
                self.process_queue()  # recursive-ish via interval?
                return False  # Stop this interval
            else:
                self.is_typing = False
                return False  # Stop interval

    def finalize_active_text(self):
        """Move active text to history log."""
        active_widget = self.get_widget_by_id("active_text")
        # We assume active widget holds the self.current_type_message fully now
        # But wait, renderable might differ if we used markup.
        # For this prototype we assume plain text or provided markup works.
        # RichLog handles markup.
        history_log = self.query_one(RichLog)
        history_log.write(self.current_type_message)
        active_widget.update("")

    def on_input_submitted(self, message: Input.Submitted) -> None:
        command = message.value.strip()
        if not command:
            return

        self.query_one(Input).value = ""

        # If user types while we are typing, should we skip to end?
        if self.is_typing:
            # Skip animation: finish it immediately
            self.finalize_active_text()
            self.is_typing = False
            self.typing_queue = []  # Clear queue to stop further typing
        elif hasattr(self, "current_type_message") and self.current_type_message:
            # Just in case some text was left hanging
            self.finalize_active_text()

        # Simplified strategy:
        # ALWAYS finalize active text before processing new input.
        if hasattr(self, "current_type_message") and self.current_type_message:
            self.finalize_active_text()
            self.current_type_message = ""  # Clear it

        log = self.query_one(RichLog)
        log.write(f"> [bold yellow]{command}[/bold yellow]")

        # Handle Slash Commands
        if command.startswith("/"):
            self.handle_slash_command(command)
            return

        if command.lower() in ["quit", "exit"]:
            self.exit()
            return

        response = self.engine.process_command(command)
        self.log_message(response)

    def handle_slash_command(self, command: str):
        cmd = command.lower()
        if cmd == "/help":
            help_text = """
[bold cyan]Available Commands:[/bold cyan]
- [bold]Movement[/bold]: go north, SOUTH, in, out...
- [bold]Actions[/bold]: look (l), inventory (i)
- [bold]System[/bold]: quit, exit
- [bold]Slash[/bold]: /help, /learn

[italic]Pro-tip: Use TAB to autocomplete common commands.[/italic]
            """
            self.log_message(help_text)

        elif cmd == "/learn":
            learn_text = """
[bold magenta]About AdventureGPT[/bold magenta]
This is a modern re-implementation of the 1976 Colossal Cave Adventure.
It uses a Python-based engine with SQLite persistence.
Phase 2 will introduce AI-generated dynamic content.
            """
            self.log_message(learn_text)
        else:
            self.log_message(f"[red]Unknown slash command: {cmd}[/red]")
