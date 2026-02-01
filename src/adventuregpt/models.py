from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Inventory(BaseModel):
    items: List[str] = Field(default_factory=list)


class PlayerState(BaseModel):
    current_room: str = "start"
    inventory: Inventory = Field(default_factory=Inventory)


class Room(BaseModel):
    description: str
    exits: Dict[str, str] = Field(default_factory=dict)
    items: List[str] = Field(default_factory=list)


class WorldState(BaseModel):
    # For now, simple key-value flags, but can be expanded
    flags: Dict[str, str] = Field(default_factory=dict)
