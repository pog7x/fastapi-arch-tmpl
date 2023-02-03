from collections import deque
from typing import Any, Callable, Dict, List, TypeVar

from faker import Faker
from pydantic import BaseModel
from pydantic_factories import AsyncPersistenceProtocol, Ignore, ModelFactory

from app.core.session import async_session
from app.models.coffee import Coffee
from app.models.user import User
from app.schemas import CoffeeModel, UserModel

fake = Faker()

T = TypeVar("T", bound=BaseModel)


class AsyncPersistenceHandler(AsyncPersistenceProtocol[T]):
    def __init__(self, model_class):
        self._model_class = model_class

    async def save(self, data: T) -> T:
        async with async_session.begin() as session:
            item = self._model_class(**data.dict())
            session.add(item)
            return item

    async def save_many(self, data: List[T]) -> List[T]:
        if len(data) == 0:
            return data

        async with async_session.begin() as session:
            for item in data:
                item = self._model_class(**data.dict())
                session.add(item)

            return data


class CustomFactory(ModelFactory):
    __faker__ = fake

    id = Ignore()

    @classmethod
    def get_provider_map(cls) -> Dict[Any, Callable]:
        provider_map: Dict[Any, Callable] = super().get_provider_map()
        faker: Faker = cls.get_faker()
        provider_map.update(
            {
                dict: lambda: faker.pydict(value_types=["str"]),
                tuple: lambda: faker.pytuple(value_types=["str"]),
                list: lambda: faker.pylist(value_types=["str"]),
                set: lambda: faker.pyset(value_types=["str"]),
                frozenset: lambda: frozenset(faker.pylist(value_types=["str"])),
                deque: lambda: deque(faker.pylist(value_types=["str"])),
            }
        )
        return provider_map


class CoffeeFactory(CustomFactory):
    __model__ = CoffeeModel
    __async_persistence__ = AsyncPersistenceHandler(Coffee)


class UserFactory(CustomFactory):
    __model__ = UserModel
    __async_persistence__ = AsyncPersistenceHandler(User)

    coffee_id = Ignore()
