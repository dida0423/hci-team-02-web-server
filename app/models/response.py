from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import uuid

class PressResponse(BaseModel):
    id: str
    name: str
    logo_img_src: str

class AuthorResponse(BaseModel):
    id: str
    name: str
    press: PressResponse

class NewsChatResponse(BaseModel):
    id: uuid.UUID
    speaker: int
    speaker_name: str
    content: str
    order: int

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
    author: AuthorResponse
    chat_lines: Optional[List[NewsChatResponse]]


    class Config:
        orm_mode = True
