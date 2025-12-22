import os
import httpx
import logging

from services.retry import retry_with_backoff
from services.rate_limit import RateLimiter

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")

if not API_BASE_URL:
    raise RuntimeError("API_BASE_URL not set")

# Allow 2 requests per second
rate_limiter = RateLimiter(rate_per_sec=2.0)


async def _fetch_products(skip: int, limit: int) -> dict:
    await rate_limiter.wait()

    headers = {
        "Authorization": f"Bearer {API_KEY}",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{API_BASE_URL}/products",
            params={"skip": skip, "limit": limit},
            headers=headers,
        )

        # Retryable failures
        if resp.status_code >= 500:
            raise RuntimeError(f"Server error {resp.status_code}")

        # Non-retryable failures
        if resp.status_code >= 400:
            logger.error(f"Non-retryable error {resp.status_code}: {resp.text}")
            resp.raise_for_status()

        return resp.json()


async def fetch_products(skip: int, limit: int) -> dict:
    return await retry_with_backoff(
        lambda: _fetch_products(skip, limit),
        retries=4,
        base_delay=0.5,
        max_delay=8.0,
    )
