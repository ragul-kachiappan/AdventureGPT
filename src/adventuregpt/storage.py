import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer

from .models import Inventory, PlayerState


def get_db_path() -> str:
    app_dir = typer.get_app_dir("adventuregpt")
    os.makedirs(app_dir, exist_ok=True)
    return str(Path(app_dir) / "adventure.db")


class GameStorage:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path if db_path else get_db_path()
        self._init_db()

    @contextmanager
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    current_room TEXT NOT NULL,
                    inventory TEXT DEFAULT '[]'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS world_state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def new_game(self, initial_state: PlayerState):
        with self._get_conn() as conn:
            conn.execute("DELETE FROM player")
            conn.execute("DELETE FROM world_state")
            conn.execute(
                "INSERT INTO player (id, current_room, inventory) VALUES (1, ?, ?)",
                (initial_state.current_room, json.dumps(initial_state.inventory.items)),
            )
            conn.commit()

    def save_player_state(self, state: PlayerState):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO player (id, current_room, inventory) VALUES (1, ?, ?)",
                (state.current_room, json.dumps(state.inventory.items)),
            )
            conn.commit()

    def load_player_state(self) -> Optional[PlayerState]:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT current_room, inventory FROM player WHERE id = 1"
            ).fetchone()
            if row:
                return PlayerState(
                    current_room=row["current_room"],
                    inventory=Inventory(items=json.loads(row["inventory"])),
                )
            return None

    def set_world_flag(self, key: str, value: Any):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO world_state (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
            conn.commit()

    def get_world_flag(self, key: str) -> Any:
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM world_state WHERE key = ?", (key,)
            ).fetchone()
            if row:
                return json.loads(row["value"])
            return None
