import logging
import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.csv_schema import CSVProduct
from schemas.models import RawCSVData, UnifiedRecord, IngestionCheckpoint

logger = logging.getLogger(__name__)

SOURCE_NAME = "products_csv"
CSV_PATH = Path("data/products.csv")


async def ingest_csv_data(session: AsyncSession) -> None:
    logger.warning("CSV INGESTION STARTED")
    logger.warning(f"CSV path resolved to: {CSV_PATH.resolve()}")
    logger.warning(f"CSV file exists: {CSV_PATH.exists()}")

    if not CSV_PATH.exists():
        logger.error("CSV file not found inside container. Skipping CSV ingestion.")
        return

    checkpoint = await session.scalar(
        select(IngestionCheckpoint).where(IngestionCheckpoint.source == SOURCE_NAME)
    )

    processed_ids = set()
    if checkpoint and checkpoint.last_processed_marker:
        processed_ids = set(checkpoint.last_processed_marker.split(","))

    new_processed_ids = set()

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                product = CSVProduct(**row)
            except Exception as e:
                logger.warning(f"Skipping invalid CSV row: {row} | error: {e}")
                continue

            if str(product.product_id) in processed_ids:
                continue

            session.add(
                RawCSVData(
                    source=SOURCE_NAME,
                    payload=row,
                )
            )

            session.add(
                UnifiedRecord(
                    source=SOURCE_NAME,
                    external_id=str(product.product_id),
                    name=product.name,
                    category=product.category,
                    value=product.price,
                    event_timestamp=datetime.now(timezone.utc),
                )
            )

            new_processed_ids.add(str(product.product_id))

    if not new_processed_ids:
        logger.warning("No new CSV records ingested")
        return

    merged_ids = sorted(processed_ids | new_processed_ids)

    if checkpoint:
        checkpoint.last_processed_marker = ",".join(merged_ids)
    else:
        session.add(
            IngestionCheckpoint(
                source=SOURCE_NAME,
                last_processed_marker=",".join(merged_ids),
            )
        )

    logger.warning(
        f"CSV INGESTION COMPLETED — records added: {len(new_processed_ids)}"
    )
