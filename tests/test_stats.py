import pytest
import socket


def db_reachable() -> bool:
    try:
        socket.gethostbyname("db")
        return True
    except socket.error:
        return False


@pytest.mark.asyncio
@pytest.mark.skipif(not db_reachable(), reason="Database not reachable outside Docker")
async def test_stats_endpoint(client):
    resp = await client.get("/stats")
    assert resp.status_code == 200

    data = resp.json()
    assert "runs" in data
    assert "records" in data
    assert "checkpoints" in data
