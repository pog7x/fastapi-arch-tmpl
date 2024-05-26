from functools import wraps

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.POSTGRES_DATABASE_URI,
    echo=settings.DEBUG,
    future=True,
)


class WithAsyncSessionMixin:
    def begin_(self):
        raise NotImplementedError

    def __call__(self, func):
        """
        Decorate function, produce new transaction,
        create and pass session to arguments

        e.g.::
            with_session = WithSessionmaker(session_maker=sessionmaker(some_engine), class_=AsyncSession)

            @with_session
            async def some_function(session):
                session.add(new_item1)
                session.add(new_item2)

            # commits transaction, closes session
        """

        @wraps(func)
        async def wrapped(*args, **kwargs):
            if self._in_arguments(*args, **kwargs):
                return await func(*args, **kwargs)

            async with self.begin_() as session:
                return await func(*args, **kwargs, session=session)

        return wrapped

    def _in_arguments(self, *args, **kwargs) -> bool:
        in_kwargs = any(isinstance(kwargv, AsyncSession) for kwargv in kwargs.values())
        in_args = any(isinstance(arg, AsyncSession) for arg in args)
        return in_kwargs or in_args


class WithAsyncSessionmaker(WithAsyncSessionMixin):
    def __init__(self, session_maker: sessionmaker) -> None:
        self._session_maker = session_maker

    def begin_(self):
        """
        Produce a context manager that both provides a new
        :class:`AsyncSession` as well as a transaction that commits.

        e.g.::
            with_session = WithAsyncSessionmaker(session_maker=sessionmaker(engine))

            async with with_session.begin_() as session:
                session.add(new_item)

            # commits transaction, closes session

        """
        return self._session_maker.begin()


class WithAsyncSession(AsyncSession, WithAsyncSessionMixin):
    def begin_(self):
        """
        Produce a context manager that both provides a new
        :class:`AsyncSession` as well as a transaction that commits.

        Easy to replace with session from `WithAsyncSessionmaker`.

        e.g.::
            with_session = WithAsyncSession(bind=engine)

            async with with_session.begin_() as session:
                session.add(new_item)

            # commits transaction, closes session

        """
        return self._maker_context_manager()


_sessionmaker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
with_session = WithAsyncSessionmaker(session_maker=_sessionmaker)
