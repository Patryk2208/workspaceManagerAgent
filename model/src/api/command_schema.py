from typing import Union
from pydantic import BaseModel, Field
from datetime import time

from .grid_system_schema import GridPosition

class AlterCommand(BaseModel):
    window_id: int = Field(ge=0, description="id of the window to perform the action on")
    position: GridPosition = Field(description="position of the window in a 6x4 grid system")

class MinimizeCommand(BaseModel):
    window_id: int = Field(ge=0, description="id of the window to perform the action on")

class Command(BaseModel):
    command_type: Union[AlterCommand, MinimizeCommand] = Field(description="type of command to perform")

class CommandPayload(BaseModel):
    command_timestamp: time = Field(description="timestamp of the command")
    commands: list[Command] = Field(description="list of commands to perform")