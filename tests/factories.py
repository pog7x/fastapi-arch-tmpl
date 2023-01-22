import factory
from faker import Faker

from app.core.session import async_session
from app.models import Item, User

rus_faker = Faker(locale="ru_RU")


class CustomFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = 'commit'

    @classmethod
    def _save(cls, model_class, session, args, kwargs):

        async def create_coro(*a, **kw) -> None:
            o = model_class(*a, **kw)
            session.add(o)
            await session.commit()
            return o

        return create_coro(*args, **kwargs)


class UserFactory(CustomFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda n: n)
    name = rus_faker.first_name()
    surname = rus_faker.last_name()
    email = rus_faker.email()
    is_active = True
    is_superuser = False


class ItemFactory(CustomFactory):
    class Meta:
        model = Item

    id = factory.Sequence(lambda n: n)
    title = rus_faker.pystr()
    description = rus_faker.sentence()
    owner = factory.SubFactory(UserFactory)
