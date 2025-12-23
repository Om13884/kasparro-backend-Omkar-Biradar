import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from ingestion.api_source.client import fetch_products
from schemas.models import RawAPIData, UnifiedRecord, IngestionCheckpoint
from schemas.run_models import ETLRun
from schemas.schema_models import SchemaSnapshot
from services.schema_drift import extract_schema_signature, diff_schemas

logger = logging.getLogger(__name__)

BATCH_SIZE = 200
SOURCE_NAME = "coingecko_api"


async def ingest_api_data(session: AsyncSession) -> None:
    run = ETLRun(source=SOURCE_NAME, status="running")
    session.add(run)
    await session.flush()

    try:
        checkpoint = await session.scalar(
            select(IngestionCheckpoint).where(
                IngestionCheckpoint.source == SOURCE_NAME
            )
        )

        skip = int(checkpoint.last_processed_marker) if checkpoint else 0

        data = await fetch_products(skip=skip, limit=BATCH_SIZE)
        coins = data.get("coins", [])

        # ---------- Schema Drift Detection ----------
        current_schema = extract_schema_signature(data)

        snapshot = await session.scalar(
            select(SchemaSnapshot).where(
                SchemaSnapshot.source == SOURCE_NAME
            )
        )

        if snapshot:
            diff = diff_schemas(snapshot.schema_signature, current_schema)
            if diff["change_score"] > 0:
                logger.warning(
                    f"SCHEMA DRIFT DETECTED for {SOURCE_NAME}: {diff}"
                )
            snapshot.schema_signature = current_schema
        else:
            session.add(
                SchemaSnapshot(
                    source=SOURCE_NAME,
                    schema_signature=current_schema,
                )
            )
        # -------------------------------------------

        if not coins:
            run.status = "success"
            return

        session.add(
            RawAPIData(
                source=SOURCE_NAME,
                payload=data,
            )
        )

        # ✅ DATABASE-LEVEL IDEMPOTENCY (FINAL FIX)
        rows = [
            {
                "source": SOURCE_NAME,
                "external_id": coin["id"],
                "name": coin.get("name"),
                "category": coin.get("symbol"),
                "value": 0.0,
                "event_timestamp": datetime.now(timezone.utc),
            }
            for coin in coins
        ]

        stmt = (
            insert(UnifiedRecord)
            .values(rows)
            .on_conflict_do_nothing(
                index_elements=["source", "external_id"]
            )
        )

        result = await session.execute(stmt)

        new_skip = skip + len(coins)

        if checkpoint:
            checkpoint.last_processed_marker = str(new_skip)
        else:
            session.add(
                IngestionCheckpoint(
                    source=SOURCE_NAME,
                    last_processed_marker=str(new_skip),
                )
            )

        run.status = "success"
        logger.warning(
            f"COINGECKO INGESTION COMPLETED — attempted {len(rows)} records"
        )

    except Exception as e:
        run.status = "failed"
        run.error_message = str(e)
        logger.exception("CoinGecko ingestion failed")
