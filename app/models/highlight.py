# app/models/highlight.py
from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.article import Article

class HighlightedArticle(Base):
    __tablename__ = 'highlighted_articles'

    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), primary_key=True)
    highlighted_text = Column(Text, nullable=False)

    article = relationship(Article, backref="highlighted_version")
