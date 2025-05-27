from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID

class StorySummary(Base):
    __tablename__ = "story_summary"

    id = Column(UUID(as_uuid=True), unique=True, primary_key=True)
    article_id = Column(UUID, ForeignKey("articles.id"), nullable=False)
    story = Column(String, nullable=False)
    dictionary = Column(JSON, nullable=False)

    article = relationship("Article", back_populates="story_summary")


    def __repr__(self):
        return f"<StorySummary(article_id={self.article_id}, dict={self.dictionary}, order={self.order})>"
