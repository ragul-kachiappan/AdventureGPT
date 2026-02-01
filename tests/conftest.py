import os
import tempfile

import pytest

from adventuregpt.engine import GameEngine


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        db_path = tmp.name
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def engine(temp_db):
    return GameEngine(db_path=temp_db)
