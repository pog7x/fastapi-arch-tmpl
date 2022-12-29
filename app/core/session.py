from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from functools import wraps
from app.models import Client
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()


class WithSession:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    def __call__(self, func):
        @wraps(func)
        async def wrapped(_, *args, **kwargs):
            async with self._session_maker.begin() as session:
                try:
                    result = await func(session, *args, **kwargs)
                except Exception as e:
                    await session.rollback()
                    raise e
                return result
        return wrapped