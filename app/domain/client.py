from typing import Optional

from pydantic import BaseModel, PositiveInt, constr


class ClientModel(BaseModel):
    id: Optional[PositiveInt]
    name: Optional[constr(min_length=2, max_length=50)]
    surname: Optional[constr(min_length=2, max_length=50)]
    credit_card: Optional[constr(min_length=2, max_length=50)]
    car_number: Optional[constr(min_length=10, max_length=15)]

    class Config:
        orm_mode = True
