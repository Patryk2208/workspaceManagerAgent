from typing import Union
from pydantic import BaseModel, Field
from time import time

from .grid_system_schema import GridPosition

class AlterCommand(BaseModel):
    """Alter command to move or resize a window."""
    window_id: int = Field(ge=0, description="id of the window to perform the action on")
    position: GridPosition = Field(description="position of the window in a 6x4 grid system")

class MinimizeCommand(BaseModel):
    """Minimize command to minimize a window."""
    window_id: int = Field(ge=0, description="id of the window to perform the action on")

class Command(BaseModel):
    """Command to perform."""
    command_type: Union[AlterCommand, MinimizeCommand] = Field(description="type of command to perform")

class CommandPayload(BaseModel):
    """Payload of the command message, containing a list of commands to perform, one for each window."""
    command_timestamp: time = Field(description="timestamp of the command")
    commands: list[Command] = Field(description="list of commands to perform")


def validate_command_payload(command_payload: CommandPayload) -> CommandPayload:
    """
    Validate action data with proper error handling.

    Returns:
        Validated ActionPayload or None if validation fails
    """
    #todo