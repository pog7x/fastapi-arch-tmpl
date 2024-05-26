from typing import List, TypeVar

from faker import Faker
from polyfactory import AsyncPersistenceProtocol, Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from app.core.session import async_session
from app.models.coffee import Coffee
from app.models.user import User

fake = Faker()

T = TypeVar("T", bound=BaseModel)


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    def __init__(self, model_class):
        self._model_class = model_class

    async def save(self, data: T) -> T:
        async with async_session.begin() as session:
            item = self._model_class(**data.model_dump())
            session.add(item)
            return item

    async def save_many(self, data: List[T]) -> List[T]:
        if len(data) == 0:
            return data

        async with async_session.begin() as session:
            for data_item in data:
                item = self._model_class(**data_item.model_dump())
                session.add(item)

            return data


class CoffeeFactory(ModelFactory):
    __faker__ = fake
    __model__ = Coffee
    __async_persistence__ = AsyncPersistenceHandler(Coffee)

    id = Ignore()


class UserFactory(ModelFactory):
    __faker__ = fake
    __model__ = User
    __async_persistence__ = AsyncPersistenceHandler(User)

    id = Ignore()
    coffee_id = Ignore()
