from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID

class NewsChat(Base):
    __tablename__ = "newschat"

    id = Column(UUID(as_uuid=True), primary_key=True)
    article_id = Column(UUID, ForeignKey("articles.id"), nullable=False)
    speaker = Column(String(50), nullable=False)
    line = Column(String(200), nullable=False)
    order = Column(Integer, nullable=False)

    article = relationship("Article", back_populates="chat_lines")

    __table_args__ = (
        UniqueConstraint("article_id", "order", name="uq_newschat_article_order"),
    )

    def __repr__(self):
        return f"<NewsChat(article_id={self.article_id}, speaker={self.speaker}, order={self.order})>"
