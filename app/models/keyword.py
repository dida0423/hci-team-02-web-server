# app/models/keyword.py
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
import uuid
from datetime import datetime

class KeywordSummary(Base):
    __tablename__ = 'keyword_summaries'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(DateTime, unique=True, nullable=False)
    keywords = Column(JSON, nullable=False)
