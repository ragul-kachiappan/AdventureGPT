def test_new_game(engine):
    desc = engine.start_new_game()
    assert "brick building" in desc
    assert engine.state.current_room == "start"


def test_movement(engine):
    engine.start_new_game()
    resp = engine.process_command("go in")
    assert "well house" in resp
    assert engine.state.current_room == "building"

    resp = engine.process_command("south")
    assert "end of a road" in resp
    assert engine.state.current_room == "start"


def test_invalid_move(engine):
    engine.start_new_game()
    resp = engine.process_command("go west")
    assert "can't go that way" in resp
    assert engine.state.current_room == "start"


def test_persistence(engine, temp_db):
    engine.start_new_game()
    engine.process_command("go in")
    assert engine.state.current_room == "building"

    # Create a new engine instance pointing to same DB
    from adventuregpt.engine import GameEngine

    new_engine = GameEngine(db_path=temp_db)
    desc = new_engine.resume_game()

    assert "well house" in desc
    assert new_engine.state.current_room == "building"


def test_inventory_empty(engine):
    engine.start_new_game()
    resp = engine.process_command("inventory")
    assert "not carrying anything" in resp
