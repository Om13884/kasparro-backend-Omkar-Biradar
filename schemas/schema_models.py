from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func

from core.db import Base


class SchemaSnapshot(Base):
    __tablename__ = "schema_snapshots"

    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False, unique=True)
    schema_signature = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
