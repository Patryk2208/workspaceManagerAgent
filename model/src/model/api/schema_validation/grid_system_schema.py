from wsgiref.validate import validator

from pydantic import BaseModel, Field, model_validator
from model.config import config

class GridPosition(BaseModel):
    """Object representing the window's position on a screen as on a grid"""
    tl: int = Field(ge=0, le=config.grid_rows - 1, description="top-left coordinate in a nxm grid system")
    br: int = Field(ge=0, le=config.grid_cols - 1, description="bottom-right coordinate in a nxm grid system")

    @model_validator(mode="after")
    def check_tl_br(cls, values):
        """
        Verifies that the position is structurally correct.
        """
        tl = values["tl"]
        br = values["br"]
        n = config.grid_rows
        m = config.grid_cols
        if tl == br and tl == n*m-1:
            return values
        if (tl / n) >= (br / n):
            raise ValueError("tl must be above br")
        if (tl % n) >= (br % n):
            raise ValueError("tl must be to the left of br")
        return values