import logging
import csv
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from schemas.csv_schema import CSVProduct
from schemas.models import RawCSVData, UnifiedRecord, IngestionCheckpoint
from schemas.run_models import ETLRun

logger = logging.getLogger(__name__)

SOURCE_NAME = "products_csv"
CSV_PATH = Path("data/products.csv")


async def ingest_csv_data(session: AsyncSession) -> None:
    logger.warning("CSV INGESTION STARTED")
    logger.warning(f"CSV path resolved to: {CSV_PATH.resolve()}")
    logger.warning(f"CSV file exists: {CSV_PATH.exists()}")

    run = ETLRun(source=SOURCE_NAME, status="running")
    session.add(run)
    await session.flush()

    duplicate_count = 0

    if not CSV_PATH.exists():
        logger.error("CSV file not found inside container. Skipping CSV ingestion.")
        run.status = "failed"
        run.error_message = "CSV file not found"
        return

    try:
        checkpoint = await session.scalar(
            select(IngestionCheckpoint).where(
                IngestionCheckpoint.source == SOURCE_NAME
            )
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
                except ValidationError as e:
                    logger.warning(
                        f"Skipping invalid CSV row: {row} | validation error: {e}"
                    )
                    continue
                except Exception as e:
                    logger.error(
                        f"Unexpected CSV error: {row} | error: {e}"
                    )
                    continue

                if str(product.product_id) in processed_ids:
                    continue

                session.add(
                    RawCSVData(
                        source=SOURCE_NAME,
                        payload=row,
                    )
                )

                try:
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
                    await session.flush()

                except IntegrityError:
                    await session.rollback()
                    duplicate_count += 1
                    continue

                new_processed_ids.add(str(product.product_id))

        if not new_processed_ids:
            run.status = "success"
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

        run.status = (
            "success_with_duplicates"
            if duplicate_count > 0
            else "success"
        )

        logger.warning(
            f"CSV INGESTION COMPLETED — records added: {len(new_processed_ids)}, "
            f"duplicates skipped: {duplicate_count}"
        )

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        logger.exception("CSV ingestion failed unexpectedly")
