from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.POSTGRES_DATABASE_URI,
    echo=settings.DEBUG,
    future=True,
)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()


class WithSession:
    def __init__(self, _session: AsyncSession) -> None:
        self._session = _session

    def __call__(self, func):
        @wraps(func)
        async def wrapped(*args, **kwargs):
            in_kwargs = any(self.is_async_session(kwargv) for kwargv in kwargs.values())
            in_args = any(self.is_async_session(arg) for arg in args)

            if in_kwargs or in_args:
                return await func(*args, **kwargs)

            try:
                result = await func(*args, **kwargs, session=self._session)
                await self._session.commit()
            except Exception as e:
                await self._session.rollback()
                raise e

            return result

        return wrapped

    def is_async_session(self, instance):
        return isinstance(instance, AsyncSession)


with_session = WithSession(_session=session)
