from typing import List, Optional

from app.models.user import User
from app.schemas import ItemModel
from app.schemas.base import sqlalchemy_to_pydantic

UserModel = sqlalchemy_to_pydantic(User, optional=["id"])


class UserWithItemsModel(UserModel):
    items: Optional[List[ItemModel]] = None
