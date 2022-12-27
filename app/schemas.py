from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt, constr, validator


class ClientModel(BaseModel):
    id: Optional[PositiveInt]
    name: constr(min_length=2, max_length=50)
    surname: constr(min_length=2, max_length=50)
    credit_card: constr(min_length=2, max_length=50)
    car_number: constr(min_length=10, max_length=15)

    class Config:
        orm_mode = True


class ParkingModel(BaseModel):
    id: Optional[PositiveInt]
    address: constr(min_length=2, max_length=100)
    opened: bool
    count_places: PositiveInt
    count_available_places: PositiveInt

    class Config:
        orm_mode = True

    @validator("count_available_places")
    def available_less_than_all(cls, v, values, **kwargs):
        if "count_places" in values and v > values["count_places"]:
            raise ValueError("count_available_places greater than count_places")
        return v


class ClientParkingModel(BaseModel):
    id: Optional[PositiveInt]
    client_id: PositiveInt
    parking_id: PositiveInt

    class Config:
        orm_mode = True


class TakeClientParkingModel(ClientParkingModel):
    time_in: datetime = None

    @validator("time_in", pre=True, always=True)
    def time_in_now(cls, v):
        return v or datetime.now()


class ReleaseClientParkingModel(ClientParkingModel):
    time_out: datetime = None

    @validator("time_out", pre=True, always=True)
    def time_in_now(cls, v):
        return v or datetime.now()
