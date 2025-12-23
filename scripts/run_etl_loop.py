import sys
from pathlib import Path
import os

# Add project root to PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Fail fast if still misconfigured
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

import asyncio
import time
from core.db import AsyncSessionLocal
from services.api_ingestion import ingest_api_data
from services.csv_ingestion import ingest_csv_data
from services.vendor_ingestion import ingest_vendor_data

INTERVAL_SECONDS = 3600  # 1 hour


async def run():
    while True:
        async with AsyncSessionLocal() as session:
            await ingest_api_data(session)
            await session.commit()   # 🔥 REQUIRED
            session.expunge_all()

        async with AsyncSessionLocal() as session:
            await ingest_csv_data(session)
            await session.commit()
            session.expunge_all()

        async with AsyncSessionLocal() as session:
            await ingest_vendor_data(session)
            await session.commit()

        print("ETL cycle completed. Sleeping...")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    asyncio.run(run())
