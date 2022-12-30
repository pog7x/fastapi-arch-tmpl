from app.models import Client
from app.repository.base_repository import BaseRepository


class ClientRepository(BaseRepository):
    model_cls = Client
