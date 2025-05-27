from fastapi import FastAPI, APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.models import NewsChat, Author, Article, Press
from app.models.response import ArticleResponse
import uuid
from app.api.deps import SessionDep
from sqlalchemy import select
import json
from app.core.db import create_news_chat, create_keyword_summary, create_highlighted_article, update_article_bias
from typing import List
from fastapi import Body

router = APIRouter(prefix="/article", tags=["article"])

@router.get("/page{page}", response_model=list[ArticleResponse])
def get_articles(page: int, session: SessionDep):
    """
    Get article by id
    """
    page -= 1
    if page < 0 or page > 3:
        raise HTTPException(status_code=400, detail="Page must be between 1 and 4")
    # select all articles with authors and press
    articles = session.query(Article).options(
        joinedload(Article.author).joinedload(Author.press)
    ).offset(page * 10).limit(10).all()

    for article in articles:
        print(article)

    return articles

@router.get("/{id}")
def get_article(id: uuid.UUID, session: SessionDep):
    """
    Get article by id
    """
    retrieve_statement = (
        select(Article)
        .where(Article.id == id)
    )

    article = session.execute(retrieve_statement).scalars().first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return article

@router.get("/view/{id}", response_model=ArticleResponse)
def get_article_summary(id: uuid.UUID, session: SessionDep):
    """
    Get article summary by id
    """
    retrieve_statement = (
        select(Article)
        .where(Article.id == id)
    )

    article = session.execute(retrieve_statement).scalars().first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    retrieve_statement = (
        select(NewsChat)
        .where(NewsChat.article_id == id)
    )

    chat_lines = session.execute(retrieve_statement).scalars().all()

    if not chat_lines:
        print("generating summary")
        create_news_chat(article, session)
        session.refresh(article)
    else:
        print("summary found!")
    
    return article

# 오늘의 키워드
@router.post("/keywords")
def get_today_keywords(session: SessionDep):
    try:
        result = create_keyword_summary(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword generation failed: {e}")
    return result

# 집중 읽기 모드
@router.get("/highlight/{id}")
def get_highlighted_article(id: uuid.UUID, session: SessionDep):
    article = session.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    try:
        highlighted = create_highlighted_article(article, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Highlight generation failed: {e}")
    
    return {"highlighted": highlighted}

# 편향
@router.get("/bias/{id}")
def get_article_bias(id: uuid.UUID, session: SessionDep):
    article = session.query(Article).filter(Article.id == id).first()

    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    try:
        result = update_article_bias(article, session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {e}")

    return result
