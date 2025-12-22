import logging
from fastapi import FastAPI
from sqlalchemy import text

from core.db import engine, Base, AsyncSessionLocal

# FORCE MODEL REGISTRATION (MANDATORY)
from schemas.run_models import ETLRun
from schemas.schema_models import SchemaSnapshot
from schemas.models import (
    RawAPIData,
    RawCSVData,
    UnifiedRecord,
    IngestionCheckpoint,
)

from services.api_ingestion import ingest_api_data
from services.csv_ingestion import ingest_csv_data
from services.vendor_ingestion import ingest_vendor_data
from services.stats_service import get_stats


logging.basicConfig(level=logging.WARNING)

app = FastAPI(
    title="Kasparro Backend & ETL",
    version="0.1.0",
)


@app.on_event("startup")
async def startup() -> None:
    # 1. Create ALL tables (ORM models must be imported above)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Run ALL ingestions in a single transactional session
    async with AsyncSessionLocal() as session:
        await ingest_api_data(session)
        await ingest_csv_data(session)
        await ingest_vendor_data(session)
        await session.commit()


@app.get("/health")
async def health() -> dict:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "database": db_status,
    }


@app.get("/stats")
async def stats() -> dict:
    async with AsyncSessionLocal() as session:
        return await get_stats(session)
