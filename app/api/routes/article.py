from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models.article import Article
from app.models.author import Author
from app.models.press import Press
from app.models.response import ArticleResponse
import uuid
from app.api.deps import SessionDep
from sqlalchemy import select
import json

router = APIRouter(prefix="/article", tags=["article"])

@router.get("/page{page}", response_model=list[ArticleResponse])
def get_articles(page: int, db: SessionDep):
    """
    Get article by id
    """
    page -= 1
    if page < 0 or page > 3:
        raise HTTPException(status_code=400, detail="Page must be between 1 and 4")
    # select all articles with authors and press
    articles = db.query(Article).options(
        joinedload(Article.author).joinedload(Author.press)
    ).offset(page * 10).limit(10).all()

    for article in articles:
        print(article)

    return articles



@router.get("/{id}")
def get_article(id: uuid.UUID, db: SessionDep):
    """
    Get article by id
    """
    retrieve_statement = (
        select(Article)
        .where(Article.id == id)
    )

    article = db.execute(retrieve_statement).scalars().first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article

