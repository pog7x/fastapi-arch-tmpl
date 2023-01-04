from fastapi import APIRouter

from app import domain
from app.models import ClientParking
from app.services.client_parking_service import ClientParkingService

router = APIRouter()


@router.post("")
async def take_parking(client_parking: domain.TakeClientParkingModel) -> ClientParking:
    return await ClientParkingService().take_parking(client_parking=client_parking)


@router.delete("")
async def release_parking(
    client_parking: domain.ReleaseClientParkingModel,
) -> ClientParking:
    return await ClientParkingService().release_parking(client_parking=client_parking)
