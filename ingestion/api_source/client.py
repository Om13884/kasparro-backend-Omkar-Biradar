import os
import httpx
import logging

from services.retry import retry_with_backoff
from services.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL")

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL not set")

# CoinGecko public limit ≈ 10–30 req/min → be conservative
rate_limiter = RateLimiter(rate_per_sec=0.5)


async def _fetch_coins() -> list[dict]:
    await rate_limiter.wait()

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{API_BASE_URL}/coins/list")

        if resp.status_code >= 500:
            raise RuntimeError(f"CoinGecko server error {resp.status_code}")

        if resp.status_code >= 400:
            logger.error(f"CoinGecko client error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        return resp.json()


async def fetch_products(skip: int = 0, limit: int = 200) -> dict:
    """
    Adapter to keep existing ingestion contract.
    CoinGecko /coins/list is not paginated, so slice locally.
    """
    coins = await retry_with_backoff(
        _fetch_coins,
        retries=4,
        base_delay=1.0,
        max_delay=10.0,
    )

    sliced = coins[skip : skip + limit]

    return {
        "coins": sliced,
        "total": len(coins),
        "skip": skip,
        "limit": limit,
    }
