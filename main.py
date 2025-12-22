from fastapi import FastAPI
from sqlalchemy import text

from core.db import engine, Base, AsyncSessionLocal
from services.api_ingestion import ingest_api_data
import logging

logging.basicConfig(level=logging.WARNING)


app = FastAPI(
    title="Kasparro Backend & ETL",
    version="0.1.0",
)


@app.on_event("startup")
async def startup() -> None:
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Run API ingestion
    async with AsyncSessionLocal() as session:
        await ingest_api_data(session)
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
