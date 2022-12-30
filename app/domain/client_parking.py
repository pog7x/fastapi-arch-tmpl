from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt, validator


class ClientParkingModel(BaseModel):
    id: Optional[PositiveInt]
    client_id: PositiveInt
    parking_id: PositiveInt
    time_in: datetime = None
    time_out: datetime = None

    class Config:
        orm_mode = True


class TakeClientParkingModel(ClientParkingModel):
    @validator("time_in", pre=True, always=True)
    def time_in_now(cls, v):
        return v or datetime.now()


class ReleaseClientParkingModel(ClientParkingModel):
    @validator("time_out", pre=True, always=True)
    def time_in_now(cls, v):
        return v or datetime.now()
