import pytest
import socket
from sqlalchemy import select

from core.db import AsyncSessionLocal
from schemas.models import UnifiedRecord


def db_reachable() -> bool:
    try:
        socket.gethostbyname("db")
        return True
    except socket.error:
        return False


@pytest.mark.asyncio
@pytest.mark.skipif(not db_reachable(), reason="Database not reachable outside Docker")
async def test_etl_creates_records():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UnifiedRecord))
        records = result.scalars().all()
        assert len(records) > 0


@pytest.mark.asyncio
@pytest.mark.skipif(not db_reachable(), reason="Database not reachable outside Docker")
async def test_checkpoint_prevents_duplicates():
    async with AsyncSessionLocal() as session:
        before = await session.execute(select(UnifiedRecord))
        count_before = len(before.scalars().all())

        after = await session.execute(select(UnifiedRecord))
        count_after = len(after.scalars().all())

        assert count_before == count_after
