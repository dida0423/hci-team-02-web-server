from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Author(Base):
    __tablename__ = 'authors'
    id = Column(String, primary_key=True)
    author_key = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)
    press_id = Column(String, ForeignKey('press.id'), nullable=False)
    press = relationship("Press", back_populates="authors")
    articles = relationship("Article", back_populates="author")

    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name}, press={self.press})>"