from app.models.user import User
from app.schemas.base import sqlalchemy_to_pydantic

UserModel = sqlalchemy_to_pydantic(User, optional=["id"])
