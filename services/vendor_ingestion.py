import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from schemas.vendor_schema import VendorProduct
from schemas.models import RawCSVData, UnifiedRecord, IngestionCheckpoint
from schemas.run_models import ETLRun

logger = logging.getLogger(__name__)

SOURCE_NAME = "vendors_csv"
CSV_PATH = Path("data/vendors.csv")



async def ingest_vendor_data(session: AsyncSession) -> None:
    logger.warning("VENDOR INGESTION STARTED")
    run = ETLRun(source=SOURCE_NAME, status="running")
    session.add(run)
    await session.flush()

    if not CSV_PATH.exists():
        logger.error("Vendor CSV not found")
        return

    checkpoint = await session.scalar(
        select(IngestionCheckpoint).where(IngestionCheckpoint.source == SOURCE_NAME)
    )

    processed_ids = set()
    if checkpoint and checkpoint.last_processed_marker:
        processed_ids = set(checkpoint.last_processed_marker.split(","))

    new_ids = set()

    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                product = VendorProduct(**row)
            except Exception as e:
                run.status = "failed"
                run.error_message = str(e)
                raise

                

            if product.vendor_id in processed_ids:
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
                    external_id=product.vendor_id,
                    name=product.product_name,
                    category=product.group,
                    value=product.amount,
                    event_timestamp=datetime.now(timezone.utc),
                )
            )

            new_ids.add(product.vendor_id)

    if not new_ids:
        logger.warning("No new vendor records")
        return

    merged = sorted(processed_ids | new_ids)

    if checkpoint:
        checkpoint.last_processed_marker = ",".join(merged)
    else:
        session.add(
            IngestionCheckpoint(
                source=SOURCE_NAME,
                last_processed_marker=",".join(merged),
            )
        )
    run.status = "success"

    logger.warning(f"VENDOR INGESTION COMPLETED — {len(new_ids)} records")
