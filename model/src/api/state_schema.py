from pydantic import BaseModel, Field
from datetime import datetime, time, timedelta

from .grid_system_schema import GridPosition

#sub-schemas
class ActivityStatistics(BaseModel):
    is_focused: bool = Field(description="true when the window is focused")
    last_focus_time: datetime = Field(description="last time the window was focused")
    current_focus_duration: timedelta = Field(description="time since last focus change on this window")
    total_focus_duration: timedelta = Field(description="total time the window has been focused")

#window state
class State(BaseModel):
    window_id: int = Field(ge=0, description="id of the window")
    title: str = Field(description="title and description of the window")
    position: GridPosition = Field(description="position of the window in a 6x4 grid system")
    window_activity: ActivityStatistics = Field(description="statistics about the window's activity and focus")
    workspace_number: int = Field(ge=0, le='''N - todo''', description="workspace number")

#entire message format
class StatePayload(BaseModel):
    state_timestamp: time = Field(description="timestamp of the state")
    window_states: list[State] = Field(description="list of states for all windows")