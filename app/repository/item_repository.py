from app.models.item import Item
from app.repository.base_repository import BaseRepository


class ItemRepository(BaseRepository):
    model_cls = Item
