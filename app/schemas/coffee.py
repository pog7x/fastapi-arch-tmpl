from app.models.coffee import Coffee
from app.schemas.base import sqlalchemy_to_pydantic

CoffeeModel = sqlalchemy_to_pydantic(Coffee, optional=["id"])
