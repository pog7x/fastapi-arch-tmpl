import factory
from faker import Faker

from app.core.session import async_session
from app.models import User

rus_faker = Faker(locale="ru_RU")


class CustomFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = async_session()
        sqlalchemy_session_persistence = factory.alchemy.SESSION_PERSISTENCE_COMMIT

    @classmethod
    def _save(cls, model_class, session, args, kwargs):

        async def create_coro(*a, **kw) -> None:
            item = model_class(*a, **kw)
            session.add(item)
            await session.commit()
            return item

        return create_coro(*args, **kwargs)
