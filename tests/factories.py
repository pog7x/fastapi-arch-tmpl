import factory
from faker import Faker

from app.core.session import session
from app.models import Client, Parking

rus_faker = Faker(locale="ru_RU")


class CustomFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = session


class ClientFactory(CustomFactory):
    class Meta:
        model = Client

    id = factory.LazyAttribute(lambda _: rus_faker.pyint(min_value=1))
    name = rus_faker.first_name()
    surname = rus_faker.last_name()
    credit_card = rus_faker.credit_card_number()
    car_number = rus_faker.license_plate()


class ParkingFactory(CustomFactory):
    class Meta:
        model = Parking

    id = factory.LazyAttribute(lambda _: rus_faker.pyint(min_value=1))
    address = rus_faker.address()
    opened = True
    count_places = rus_faker.pyint(min_value=10, max_value=100, step=1)
    count_available_places = factory.LazyAttribute(
        lambda x: rus_faker.pyint(min_value=1, max_value=x.count_places, step=1)
    )
