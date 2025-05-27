from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, LargeBinary, Float, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID
from app.models.author import Author
from app.models.press import Press
from app.models.newschat import NewsChat


class Article(Base):
    __tablename__ = 'articles'

    id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String(255), nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    content = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    edited_at = Column(DateTime, nullable=True)
    narrative_summary = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=True)
    image_text = Column(String, nullable=True)
    ranking = Column(Integer, nullable=False, default=0)
    activity_score = Column(Float, nullable=False, default=0)
    genre = Column(String, nullable=False, default="")
    author_id = Column(String, ForeignKey('authors.id'), nullable=False)
    press_id = Column(String, ForeignKey('press.id'), nullable=False)
    story_summary = Column(String, nullable=True)
    story_original = Column(String, nullable=True)
    author = relationship("Author", back_populates="articles")
    press = relationship("Press", back_populates="articles")
    
    media_bias = Column(String(10), nullable=True)
    reporting_bias = Column(String(10), nullable=True)

    chat_lines = relationship("NewsChat", back_populates="article")

    def __repr__(self):
        return f"<Article(id={self.id}, title={self.title}, url={self.url})>"