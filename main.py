from fastapi import FastAPI
from sqlalchemy import text
from core.db import engine
from core.db import engine, Base
from schemas.models import *
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
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
