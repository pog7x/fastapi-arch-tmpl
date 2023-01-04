from app.models import ClientParking
from app.repository.base_repository import BaseRepository


class ClientParkingRepository(BaseRepository):
    model_cls = ClientParking
