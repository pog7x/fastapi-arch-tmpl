from app.models.coffee import Coffee
from app.repository.base_repository import BaseRepository


class CoffeeRepository(BaseRepository):
    model_cls = Coffee
