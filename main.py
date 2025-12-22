from fastapi import FastAPI
from sqlalchemy import text
from core.db import engine

app = FastAPI(
    title="Kasparro Backend & ETL",
    version="0.1.0",
)


@app.get("/health")
async def health():
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
