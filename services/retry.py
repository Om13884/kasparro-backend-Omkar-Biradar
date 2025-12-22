import asyncio
import random
import logging

logger = logging.getLogger(__name__)


async def retry_with_backoff(
    func,
    *,
    retries: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    retry_exceptions: tuple = (Exception,),
):
    """
    Retry an async function with exponential backoff + jitter.
    """
    attempt = 0

    while True:
        try:
            return await func()
        except retry_exceptions as e:
            attempt += 1
            if attempt > retries:
                logger.error(f"Retry limit exceeded: {e}")
                raise

            delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
            jitter = random.uniform(0, delay * 0.1)
            sleep_for = delay + jitter

            logger.warning(
                f"Retrying ({attempt}/{retries}) after {sleep_for:.2f}s due to: {e}"
            )

            await asyncio.sleep(sleep_for)
