import pytest

from adventuregpt.engine import GameEngine
from adventuregpt.tui import AdventureApp


@pytest.mark.asyncio
async def test_tui_startup():
    engine = GameEngine()
    app = AdventureApp(engine, start_new=True)
    async with app.run_test() as pilot:
        # Check if log has content
        log = app.query_one("#game_log")
        assert "brick building" in str(log.lines)

        # input "go in"
        app.query_one("#command_input").value = "go in"
        await pilot.press("enter")

        # Check response
        assert "well house" in str(log.lines)


@pytest.mark.asyncio
async def test_tui_persistence(temp_db):
    # Setup state
    engine = GameEngine(db_path=temp_db)
    engine.start_new_game()
    engine.process_command("go in")

    # Launch app resuming game
    app = AdventureApp(GameEngine(db_path=temp_db), start_new=False)
    async with app.run_test() as pilot:
        log = app.query_one("#game_log")
        # Should show current room description immediately
        await pilot.pause()  # wait for mount maybe? run_test usually waits for mount.
        assert "well house" in str(log.lines)
