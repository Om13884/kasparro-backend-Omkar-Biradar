from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from core.db import Base


class ETLRun(Base):
    __tablename__ = "etl_runs"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)  # running | success | failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)
