import asyncio
import os

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.fixture(scope="session", autouse=True)
async def create_db_engine():
    from app.models import Base

    test_db_url = os.environ.get("DATABASE_URL")
    engine = create_async_engine(test_db_url, echo=True, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
def application() -> FastAPI:
    from app.main import app

    return app


@pytest.fixture
async def initialized_app(application: FastAPI) -> FastAPI:
    async with LifespanManager(application):
        yield application


@pytest.fixture
async def client(application: FastAPI) -> AsyncClient:
    async with LifespanManager(application):
        async with AsyncClient(
            app=application,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
            yield client


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
    asyncio.set_event_loop(asyncio.new_event_loop())
