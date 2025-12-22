from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    Float,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from core.db import Base


class RawAPIData(Base):
    __tablename__ = "raw_api_data"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())


class RawCSVData(Base):
    __tablename__ = "raw_csv_data"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())


class UnifiedRecord(Base):
    __tablename__ = "unified_records"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_source_external"),
    )


class IngestionCheckpoint(Base):
    __tablename__ = "ingestion_checkpoints"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, unique=True)
    last_processed_marker = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
