import asyncio

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient


@pytest.fixture(scope="session", autouse=True)
async def engine():
    from app.core.session import engine
    from app.models import Base

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
