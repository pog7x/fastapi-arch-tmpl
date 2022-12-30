from typing import Optional

from pydantic import BaseModel, PositiveInt, constr, validator


class ParkingModel(BaseModel):
    id: Optional[PositiveInt]
    address: Optional[constr(min_length=2, max_length=100)]
    opened: Optional[bool]
    count_places: Optional[PositiveInt]
    count_available_places: Optional[PositiveInt]

    class Config:
        orm_mode = True

    @validator("count_available_places")
    def available_less_than_all(cls, v, values, **kwargs):
        if "count_places" in values and v > values["count_places"]:
            raise ValueError("count_available_places greater than count_places")
        return v
