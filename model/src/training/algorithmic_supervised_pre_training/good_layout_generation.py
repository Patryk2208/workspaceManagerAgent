import random
from datetime import timedelta

from api.schema_validation.state_schema import State, StatePayload, ActivityStatistics
from api.schema_validation.grid_system_schema import GridPosition
from caching.pre_training_caching import PreTrainingCaching


class GoodLayoutGenerator:
    def __init__(self, max_windows : int, max_workspaces : int, grid_x : int, grid_y : int, host, port, db, password):
        self.max_windows = max_windows
        self.max_workspaces = max_workspaces
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.title_db = PreTrainingCaching(host, port, db, password)

    def generate_good_layout(self, number_of_windows : int, seed : random.seed) -> StatePayload:
        good_layout : StatePayload
        windows = []
        for i in range(number_of_windows):
            #todo good window generation
            activity = ActivityStatistics(
                is_focused=False,
                current_focus_duration=timedelta(seconds=0),
                total_focus_duration=timedelta(seconds=0)
            )
            position = GridPosition(
                tlx=random.randint(0, self.grid_x - 1),
                tly=random.randint(0, self.grid_y - 1),
                brx=random.randint(0, self.grid_x - 1),
                bry=random.randint(0, self.grid_y - 1)
            )
            workspace = random.randint(0, self.max_workspaces - 1)
            window = State(
                window_id=0,
                title="",
                position=position,
                window_activity=activity,
                workspace_number=workspace
            )
            windows.append(window)
        good_layout = StatePayload(
            state_timestamp=0,
            window_states=windows
        )
        return good_layout