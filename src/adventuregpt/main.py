import os
import shutil
from typing import Optional

import typer

from adventuregpt.engine import GameEngine
from adventuregpt.storage import get_db_path
from adventuregpt.tui import AdventureApp

app = typer.Typer(
    name="adventuregpt",
    help="A modern CLI text adventure game powered by GenAI",
    add_completion=False,
    invoke_without_command=True,  # Allow running main callback if no command
)


@app.callback()
def main(
    ctx: typer.Context,
    new: bool = typer.Option(
        False, "--new", "-n", help="Start a new game even if a save exists."
    ),
):
    """
    AdventureGPT: Text Adventure Game (TUI).
    """
    # Only run the TUI if no subcommand is invoked (like 'nuke' or 'reset')
    if ctx.invoked_subcommand is None:
        engine = GameEngine()
        app = AdventureApp(engine, start_new=new)
        app.run()


@app.command()
def reset():
    """
    Reset the game state completely.
    """
    engine = GameEngine()
    engine.start_new_game()
    typer.echo("Game reset. Run 'adventuregpt' to start fresh.")


@app.command()
def nuke():
    """
    Completely remove all game data and configuration.
    Use this before uninstalling.
    """
    db_path = get_db_path()
    parent_dir = os.path.dirname(db_path)

    if os.path.exists(parent_dir):
        confirm = typer.confirm(
            f"Are you sure you want to delete all data in {parent_dir}?"
        )
        if not confirm:
            typer.echo("Aborted.")
            return

        try:
            shutil.rmtree(parent_dir)
            typer.echo(f"Deleted {parent_dir}")
        except Exception as e:
            typer.echo(f"Error deleting data: {e}")
    else:
        typer.echo("No data found to delete.")


if __name__ == "__main__":
    app()
