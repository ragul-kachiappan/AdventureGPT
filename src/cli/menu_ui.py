from rich.style import Style
from rich.text import Text
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Center, Container
from textual.widgets import Button, Footer, Header, Static


class MenuButton(Button):
    """Custom button style for menu options"""

    def __init__(self, label: str, id: str):
        super().__init__(label, id=id)
        self.styles.width = 20
        self.styles.margin = (1, 0)
        self.styles.background = "#282828"  # Dark gray
        self.styles.color = "white"


class GameMenu(App):
    """Main menu application for Colossal Adventure"""

    CSS = """
    Screen {
        background: #141414;
    }
    
    #title {
        color: #FFD700;
        text-align: center;
        margin: 2;
    }
    
    #menu-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    Button:hover {
        background: #3c3c3c;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        yield Container(
            Static("COLOSSAL ADVENTURE", id="title"),
            Center(
                MenuButton("New Game", "new-game"),
                MenuButton("Load Game", "load-game"),
                MenuButton("Options", "options"),
                MenuButton("Exit", "exit"),
                id="menu-container",
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events"""
        button_id = event.button.id
        if button_id == "new-game":
            self.notify("Starting new game...", title="Game")
        elif button_id == "load-game":
            self.notify("Loading game...", title="Game")
        elif button_id == "options":
            self.notify("Opening options...", title="Game")
        elif button_id == "exit":
            self.exit()

    def on_key(self, event: events.Key) -> None:
        """Handle keyboard events"""
        if event.key == "escape":
            self.exit()


def run_menu():
    """Run the game menu"""
    app = GameMenu()
    app.run()


if __name__ == "__main__":
    run_menu()
