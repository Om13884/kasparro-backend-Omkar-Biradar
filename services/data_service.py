import time
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.models import UnifiedRecord


async def fetch_data(
    session: AsyncSession,
    source: str | None,
    limit: int,
    offset: int,
):
    start = time.time()
    request_id = str(uuid.uuid4())

    query = select(UnifiedRecord)

    if source:
        query = query.where(UnifiedRecord.source == source)

    query = query.limit(limit).offset(offset)

    result = await session.execute(query)
    records = result.scalars().all()

    latency_ms = int((time.time() - start) * 1000)

    return {
        "request_id": request_id,
        "api_latency_ms": latency_ms,
        "count": len(records),
        "data": [
            {
                "id": r.id,
                "source": r.source,
                "external_id": r.external_id,
                "name": r.name,
                "category": r.category,
                "value": r.value,
                "event_timestamp": r.event_timestamp.isoformat(),
            }
            for r in records
        ],
    }
