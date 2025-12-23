import asyncio
import pytest
import os
from dotenv import load_dotenv

from httpx import AsyncClient
from httpx import ASGITransport

# Load env for tests
load_dotenv()

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL not set for tests")

from main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac
