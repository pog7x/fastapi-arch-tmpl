from typing import Any, AsyncIterator, Awaitable

import pytest
from httpx import ASGITransport, AsyncClient

TestApp = Awaitable[dict[str, Any]], (dict[str, Any])


@pytest.fixture(scope="function", autouse=True)
async def engine(event_loop):
    from app.core.session import engine
    from app.models import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def application() -> TestApp:
    from app.main import app_factory

    return app_factory()


@pytest.fixture(scope="session")
async def http_client(application: TestApp) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=application),
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def base_url() -> str:
    return "http://base.url/test"
