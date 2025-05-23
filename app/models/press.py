from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, LargeBinary
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy.dialects.postgresql import UUID

class Press(Base):
    __tablename__ = 'press'
    id = Column(String, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    logo_img_src = Column(String(120), nullable=True)

    authors = relationship("Author", back_populates="press")
    articles = relationship("Article", back_populates="press")

    def __repr__(self):
        return f"<Press(id={self.id}, name={self.name})>"