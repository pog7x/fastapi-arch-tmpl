from typing import List, TypeVar

from faker import Faker
from polyfactory import AsyncPersistenceProtocol, Ignore
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel

from app.core.session import with_session
from app.models.coffee import Coffee
from app.models.user import User

fake = Faker()

T = TypeVar("T", bound=BaseModel)


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    def __init__(self, model_class):
        self._model_class = model_class

    async def save(self, data: T) -> T:
        async with with_session.begin_() as session:
            session.add(data)
            return data

    async def save_many(self, data: List[T]) -> List[T]:
        if len(data) == 0:
            return data

        async with with_session.begin_() as session:
            session.add_all(data)
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
