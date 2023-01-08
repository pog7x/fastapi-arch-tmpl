from fastapi import APIRouter
from pydantic import PositiveInt, constr

from app import domain
from app.models import Parking
from app.repository.parking_repository import ParkingRepository

router = APIRouter()


class APIParkingModel(domain.ParkingModel):
    address: constr(min_length=2, max_length=100)
    opened: bool
    count_places: PositiveInt
    count_available_places: PositiveInt


@router.post("/", response_model=domain.ParkingModel)
async def create_parking(parking: APIParkingModel) -> Parking:
    return await ParkingRepository().create_item(create_data=parking)
