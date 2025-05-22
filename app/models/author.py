from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID

# Association table for Article <-> Author (many-to-many)
article_author_table = Table(
    'article_author',
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("author_id", Integer, primary_key=True),
    Column("press_id", Integer, primary_key=True),
    ForeignKeyConstraint(["author_id", "press_id", ], ["authors.id", "authors.press_id"])
)

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    press_id = Column(Integer, ForeignKey('press.id'), primary_key=True, nullable=False)
    press = relationship("Press", back_populates="authors")

    articles = relationship(
        "Article",
        secondary=article_author_table,
        back_populates="author"
    )

    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name}, press={self.press})>"