import os
from functools import wraps
from typing import Callable
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()


class WithSession:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    def __call__(self, func):

        @wraps(func)
        async def wrapped(*args, **kwargs):
            if self.is_async_session(kwargs.get("session")):
                session = kwargs["session"]
            else:
                for a in args:
                    if self.is_async_session(a):
                        session = a
                        break
                else:
                    session = self._session_maker()

            async with session.begin():
                return await func(*args, **kwargs, session=session)

        return wrapped
    
    def is_async_session(self, instance):
        return isinstance(instance, AsyncSession)


with_session = WithSession(session_maker=async_session)
