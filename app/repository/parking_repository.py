from app.models import Parking
from app.repository.base_repository import BaseRepository


class ParkingRepository(BaseRepository):
    model_cls = Parking
