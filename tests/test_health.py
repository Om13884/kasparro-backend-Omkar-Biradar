import pytest
import socket


def db_reachable() -> bool:
    try:
        socket.gethostbyname("db")
        return True
    except socket.error:
        return False


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200

    data = resp.json()
    assert data["status"] == "ok"

    # Database may be unavailable outside Docker
    if db_reachable():
        assert data["database"] == "ok"
    else:
        assert data["database"] == "error"
