from collections import deque
from typing import Any, Callable, Dict, TypeVar

from faker import Faker
from pydantic import BaseModel
from pydantic_factories import Ignore, ModelFactory

from app.schemas import CoffeeModel, UserModel

fake = Faker()

T = TypeVar("T", bound=BaseModel)


class CustomFactory(ModelFactory):
    __faker__ = fake

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

    id = Ignore()


class UserFactory(CustomFactory):
    __model__ = UserModel

    id = Ignore()
    coffee_id = Ignore()
