from app.models.item import Item
from app.schemas.base import sqlalchemy_to_pydantic

ItemModel = sqlalchemy_to_pydantic(Item, optional=["id"])
