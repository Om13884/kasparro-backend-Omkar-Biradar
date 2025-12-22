import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from ingestion.api_source.client import fetch_products
from schemas.models import RawAPIData, UnifiedRecord, IngestionCheckpoint

logger = logging.getLogger(__name__)

BATCH_SIZE = 50
SOURCE_NAME = "dummyjson_api"


async def ingest_api_data(session: AsyncSession) -> None:
    logger.warning("INGESTION STARTED")

    checkpoint = await session.scalar(
        select(IngestionCheckpoint).where(IngestionCheckpoint.source == SOURCE_NAME)
    )

    skip = int(checkpoint.last_processed_marker) if checkpoint else 0
    logger.warning(f"Checkpoint skip value: {skip}")

    try:
        data = await fetch_products(skip=skip, limit=BATCH_SIZE)
    except Exception as e:
        logger.exception("API fetch failed")
        return

    products = data.get("products", [])
    logger.warning(f"Products fetched: {len(products)}")

    if not products:
        logger.warning("No products returned, exiting ingestion")
        return

    session.add(
        RawAPIData(
            source=SOURCE_NAME,
            payload=data,
        )
    )

    for product in products:
        session.add(
            UnifiedRecord(
                source=SOURCE_NAME,
                external_id=str(product["id"]),
                name=product["title"],
                category=product["category"],
                value=float(product["price"]),
                event_timestamp=datetime.now(timezone.utc),
            )
        )

    new_skip = skip + len(products)

    if checkpoint:
        checkpoint.last_processed_marker = str(new_skip)
    else:
        session.add(
            IngestionCheckpoint(
                source=SOURCE_NAME,
                last_processed_marker=str(new_skip),
            )
        )

    logger.warning("INGESTION COMPLETED")
