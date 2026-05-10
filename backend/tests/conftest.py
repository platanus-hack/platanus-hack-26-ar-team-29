from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient

from app.api.deps import DEV_USER_ID
from app.main import create_app

DEV_AUTH_HEADER = {"Authorization": f"Bearer dev-{DEV_USER_ID}"}
DEV_WS_TOKEN = f"dev-{DEV_USER_ID}"


@pytest.fixture(scope="session")
def app() -> Iterator[FastAPI]:
    yield create_app()


@pytest.fixture(scope="session")
def sync_client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app, headers=DEV_AUTH_HEADER) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with app.router.lifespan_context(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers=DEV_AUTH_HEADER,
        ) as client:
            yield client
