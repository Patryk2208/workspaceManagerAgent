from typing import Optional
from pydantic import BaseModel, Field
from datetime import timedelta
from time import time

from .grid_system_schema import GridPosition
from model.config import config

#sub-schemas
class ActivityStatistics(BaseModel):
    """Activity statistics for a window."""
    is_focused: bool = Field(description="true when the window is focused")
    current_focus_duration: timedelta = Field(description="time since last focus change on this window")
    total_focus_duration: timedelta = Field(description="total time the window has been focused")

#window state
class State(BaseModel):
    """State of a window."""
    window_id: int = Field(ge=0, description="id of the window")
    title: str = Field(description="title and description of the window")
    position: GridPosition = Field(description="position of the window in a 6x4 grid system")
    window_activity: ActivityStatistics = Field(description="statistics about the window's activity and focus")
    workspace_number: int = Field(ge=0, le=config.max_windows - 1, description="workspace number")

#entire message format
class StatePayload(BaseModel):
    """Payload of the state message, containing a list of states for all windows."""
    state_timestamp: float = Field(description="timestamp of the state")
    window_states: list[State] = Field(description="list of states for all windows")

def validate_state_payload(state_payload: dict) -> Optional[StatePayload]:
    """
    Validate state data with proper error handling.

    Returns:
        Validated StatePayload or None if validation fails
    """
    try:
        return StatePayload(**state_payload)
    except ValueError as e:
        print(f"Failed to validate state payload: {e}")
        return None

