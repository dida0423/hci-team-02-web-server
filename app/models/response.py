from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid

class PressResponse(BaseModel):
    id: int
    name: str
    logo_img_src: str

class AuthorResponse(BaseModel):
    id: int
    name: str
    press: PressResponse

class ArticleResponse(BaseModel):
    id: uuid.UUID
    title: str
    url: str
    content: str
    published_at: datetime
    edited_at: datetime | None
    genre: str
    activity_score: int
    ranking: int
    image_text: str | None
    author: AuthorResponse
    press: PressResponse


    class Config:
        orm_mode = True