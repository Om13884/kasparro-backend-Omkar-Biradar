import pytest

@pytest.mark.asyncio
async def test_data_endpoint(client):
    resp = await client.get("/data?limit=5")
    assert resp.status_code == 200
    body = resp.json()
    assert "request_id" in body
    assert "api_latency_ms" in body
    assert "data" in body
