from faker import Faker
from polyfactory import Ignore
from polyfactory.factories.pydantic_factory import ModelFactory

from app.schemas import CoffeeModel, UserModel

fake = Faker()


class CoffeeFactory(ModelFactory):
    __model__ = CoffeeModel
    __faker__ = fake

    id = Ignore()


class UserFactory(ModelFactory):
    __model__ = UserModel
    __faker__ = fake

    id = Ignore()
    coffee_id = Ignore()
