from pydantic import BaseModel, Field, model_validator
from model.config import config

class GridPosition(BaseModel):
    """Object representing the window's position on a screen as on a grid"""
    tlx: int = Field(ge=0, le=config.grid_rows - 1, description="top-left x coordinate in a nxm grid system")
    tly: int = Field(ge=0, le=config.grid_cols - 1, description="top-left y coordinate in a nxm grid system")
    brx: int = Field(ge=0, le=config.grid_rows - 1, description="bottom-right x coordinate in a nxm grid system")
    bry: int = Field(ge=0, le=config.grid_cols - 1, description="bottom-right y coordinate in a nxm grid system")

    @model_validator(mode="after")
    def check_tl_br(cls, values):
        """
        Verifies that the position is structurally correct.
        """
        tlx = values["tlx"]
        tly = values["tly"]
        brx = values["brx"]
        bry = values["bry"]
        n = config.grid_rows
        m = config.grid_cols
        if tlx == brx and tlx == n-1 and tly == bry and tly == m-1:
            return values
        if tly >= bry:
            raise ValueError("tl must be above br")
        if tlx >= brx:
            raise ValueError("tl must be to the left of br")
        return values