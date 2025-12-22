import asyncio
import time


class RateLimiter:
    """
    Simple async token-bucket style rate limiter.
    """

    def __init__(self, rate_per_sec: float):
        self.interval = 1.0 / rate_per_sec
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def wait(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_call
            if elapsed < self.interval:
                await asyncio.sleep(self.interval - elapsed)
            self._last_call = time.monotonic()
