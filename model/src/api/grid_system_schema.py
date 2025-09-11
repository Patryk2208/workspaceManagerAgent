from wsgiref.validate import validator

from pydantic import BaseModel, Field, model_validator

#todo make 6x4 into variables

class GridPosition(BaseModel):
    tl: int = Field(ge=0, le=5, description="top-left coordinate in a nxm grid system")
    br: int = Field(ge=0, le=3, description="bottom-right coordinate in a nxm grid system")

    @model_validator(mode="after")
    def check_tl_br(cls, values):
        tl = values["tl"]
        br = values["br"]
        n = 6
        m = 4
        if tl == br and tl == n*m-1:
            return values
        if (tl / n) >= (br / n):
            raise ValueError("tl must be above br")
        if (tl % n) >= (br % n):
            raise ValueError("tl must be to the left of br")
        return values