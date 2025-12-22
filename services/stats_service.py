from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from schemas.run_models import ETLRun
from schemas.models import IngestionCheckpoint, UnifiedRecord


async def get_stats(session: AsyncSession) -> dict:
    total_runs = await session.scalar(
        select(func.count()).select_from(ETLRun)
    )

    success_runs = await session.scalar(
        select(func.count()).where(ETLRun.status == "success")
    )

    failed_runs = await session.scalar(
        select(func.count()).where(ETLRun.status == "failed")
    )

    last_success = await session.scalar(
        select(func.max(ETLRun.finished_at)).where(ETLRun.status == "success")
    )

    last_failure = await session.scalar(
        select(func.max(ETLRun.finished_at)).where(ETLRun.status == "failed")
    )

    records_result = await session.execute(
        select(UnifiedRecord.source, func.count())
        .group_by(UnifiedRecord.source)
    )
    records_by_source = {row[0]: row[1] for row in records_result.all()}

    checkpoint_result = await session.execute(
        select(
            IngestionCheckpoint.source,
            IngestionCheckpoint.last_processed_marker,
        )
    )
    checkpoints = {row[0]: row[1] for row in checkpoint_result.all()}

    return {
        "runs": {
            "total": total_runs or 0,
            "success": success_runs or 0,
            "failed": failed_runs or 0,
            "last_success_at": last_success,
            "last_failure_at": last_failure,
        },
        "records": records_by_source,
        "checkpoints": checkpoints,
    }
