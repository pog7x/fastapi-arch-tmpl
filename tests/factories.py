import factory
from faker import Faker

from app.models import Client, Parking
from app.core.session import async_session

session = async_session()

rus_faker = Faker(locale="ru_RU")


class CustomFactory(factory.Factory):
    @classmethod
    def _create(cls, model, *args, **kwargs):
        async def create_coro(*a, **kw) -> None:
            o = model(*a, **kw)
            session.add(o)
            await session.commit()
            return o

        return create_coro(*args, **kwargs)


class ClientFactory(CustomFactory):
    class Meta:
        model = Client

    name = rus_faker.first_name()
    surname = rus_faker.last_name()
    credit_card = rus_faker.credit_card_number()
    car_number = rus_faker.license_plate()


class ParkingFactory(CustomFactory):
    class Meta:
        model = Parking

    address = rus_faker.address()
    opened = True
    count_places = rus_faker.pyint(min_value=10, max_value=100, step=1)
    count_available_places = factory.LazyAttribute(
        lambda x: rus_faker.pyint(min_value=1, max_value=x.count_places, step=1)
    )
