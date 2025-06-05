from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Direction(str, Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"


class Item(BaseModel):
    name: str
    description: str
    is_portable: bool = True
    is_visible: bool = True
    is_takeable: bool = True


class Room(BaseModel):
    id: str
    name: str
    description: str
    exits: Dict[Direction, str] = Field(default_factory=dict)
    items: List[str] = Field(default_factory=list)
    is_visible: bool = True


class PlayerState(BaseModel):
    current_room: str
    inventory: List[str] = Field(default_factory=list)
    visited_rooms: List[str] = Field(default_factory=list)
    score: int = 0
    is_lamp_on: bool = False
    is_alive: bool = True


class GameState(BaseModel):
    player: PlayerState
    rooms: Dict[str, Room] = Field(default_factory=dict)
    items: Dict[str, Item] = Field(default_factory=dict)
    game_started: bool = False
    game_over: bool = False
