from dotenv import load_dotenv
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import subprocess
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session, sessionmaker
import sys
import app.util.scraper
from app.models.article import Article
from app.models.author import Author
from app.models.press import Press
from app.models.newschat import NewsChat
from app.models.keyword import KeywordSummary
from app.models.highlight import HighlightedArticle
import uuid
from app.core.util import dotdict
import json
from typing import List

from app.util.AI import generate_chat, generate_narrative, generate_highlighted_article, generate_keywords, detect_article_bias
from datetime import datetime, timedelta

crawl_enabled = os.getenv("CRAWL", "false").lower() == "true"
db_init_enabled = os.getenv("DB", "false").lower() == "true"
article_json_path = os.getenv("ARTICLE_JSON_PATH", None)
press_id_json_path = os.getenv("PRESS_ID_JSON_PATH", None)


load_dotenv(override=True)

# Check if the environment variables are set for prod
DB_NAME = os.getenv("DB_NAME") or "hcidb"
DB_USER = os.getenv("DB_USER") or "user"
DB_HOST = os.getenv("DB_HOST") or "localhost"
DB_PORT = os.getenv("DB_PORT") or "5432"
DB_DRIVER = os.getenv("DB_DRIVER") or "postgresql+psycopg2"

DB_PASSWORD = os.getenv("DB_PASSWORD") or "postgres"

SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

API_KEY = os.getenv("API_KEY")


def initialize_database(DB_NAME: str, DB_USER: str, DB_PASSWORD: str, DB_HOST: str, DB_PORT: str) -> None:
    # Connect to default 'postgres' database
    conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # Needed to CREATE DATABASE

    cursor = conn.cursor()
    try:
        cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME};")
        print(f"Database '{DB_NAME}' dropped.")
        cursor.execute(f"CREATE DATABASE {DB_NAME};")
        print(f"Database '{DB_NAME}' created.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{DB_NAME}' already exists.")
    try:
        subprocess.run(
            [
                "alembic",
                "stamp",
                "head"
            ],
            check=True
        )
        subprocess.run(
            [
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "create database"
            ],
            check=True
        )
        subprocess.run([
            "alembic",
            "upgrade",
            "head"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running alembic revision: {e}")
    finally:
        cursor.close()
        conn.close()

def create_news_chat(article: Article, session: Session) -> List[NewsChat]:
    """
    Create a new news chat entry in the database.
    """
    chat_list = generate_chat(article, API_KEY=API_KEY)

    try:
        session.add_all(chat_list)
        session.commit()
    except Exception as e:
        print(f"Error creating news chat: {e}")
        session.rollback()

    return chat_list

def create_summary(article: Article, session: Session) -> Article:
    """
    Create a summary for the article.
    """
    try:
        story_summary = generate_narrative(article, API_KEY=API_KEY)
        session.add(story_summary)
        session.commit()
    except Exception as e:
        print("!!!!!")
        print(f"Error creating summary: {e}")
        session.rollback()

    return article

# 오늘의 키워드
def create_keyword_summary(session: Session) -> dict:
    now = datetime.now()
    start_time = now - timedelta(hours=24)

    # 24시간 이내 기사 제목 수집
    #titles = session.query(Article.title).filter(Article.published_at >= start_time).all()
    titles = session.query(Article.title).all()
    titles = [t[0] for t in titles]

    if not titles:
        return {"error": "No recent articles found."}

    today = now.date()
    existing = session.query(KeywordSummary).filter(KeywordSummary.date == today).first()

    if existing:
        print("[DEBUG] 오늘 키워드 이미 존재")
        return existing.keywords

    raw_result = generate_keywords(titles, API_KEY)
    raw_keywords = raw_result["keywords"]

    # 각 키워드에 대해 activity_score가 가장 높은 기사 ID 찾기
    keywords_with_article = []
    for item in raw_keywords:
        keyword = item["keyword"]
        score = item["score"]
        best_article = (
            session.query(Article)
            .filter(Article.title.ilike(f"%{keyword}%"))
            .order_by(Article.activity_score.desc())
            .first()
        )
        article_id = str(best_article.id) if best_article else None
        keywords_with_article.append({
            "keyword": keyword,
            "score": score,
            "article_id": article_id
        })

    keyword_entry = KeywordSummary(date=today, keywords=keywords_with_article)

    try:
        session.add(keyword_entry)
        session.commit()
    except Exception as e:
        print(f"Error saving keywords: {e}")
        session.rollback()

    return keywords_with_article

# 집중 읽기 모드
def create_highlighted_article(article: Article, session: Session) -> str:
    existing = session.query(HighlightedArticle).filter(HighlightedArticle.article_id == article.id).first()
    if existing:
        return existing.highlighted_text
    
    highlighted_text = generate_highlighted_article(article, API_KEY)

    new_entry = HighlightedArticle(article_id=article.id, highlighted_text=highlighted_text)

    try:
        session.add(new_entry)
        session.commit()
    except Exception as e:
        print(f"Error saving highlighted article: {e}")
        session.rollback()

    return highlighted_text

# 편향 감지
def update_article_bias(article: Article, session: Session) -> dict:
    # 정치 기사 확인
    if article.genre != "정치":
        return {"media_bias": None, "reporting_bias": None}
    
    if article.media_bias is not None and article.reporting_bias is not None:
        return {"media_bias": article.media_bias, "reporting_bias": article.reporting_bias}

    media_name = article.press.name
    content = article.content

    bias_result = detect_article_bias(media_name, content, API_KEY)

    article.media_bias = bias_result["media_bias"]
    article.reporting_bias = bias_result["reporting_bias"]

    try:
        session.commit()
        print("[DEBUG] 기사 편향 정보 업데이트 완료")
    except Exception as e:
        print(f"[ERROR] 편향 정보 업데이트 실패: {e}")
        session.rollback()

    return bias_result

if db_init_enabled:
    try:
        initialize_database(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
    except Exception as e:
        pass


engine = create_engine(SQLALCHEMY_DATABASE_URI)

try:
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
except Exception as e:
    print(f"Error creating session: {e}")
    exit(-1)

if crawl_enabled and session:
    try:
        try:
            initialize_database(DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
        except Exception as e:
            print(f"Error initializing database: {e}")
            pass

        if article_json_path and press_id_json_path:
            with open(article_json_path, "r", encoding="utf-8") as f:
                article_data = json.load(f)
            f.close()
            with open(press_id_json_path, "r", encoding="utf-8") as f:
                press_logo_set = json.load(f)
            f.close()
        else:
            article_data, press_logo_set = app.util.scraper.crawl()

            print("Crawling completed successfully.")

            print("Sample data (First 3):", article_data[:3])

            # Write to file
            with open("article_data.json", "w", encoding="utf-8") as f:
                json.dump(article_data, f, ensure_ascii=False, indent=4)
            f.close()
            with open("press_logo_set.json", "w") as f:
                json.dump(press_logo_set, f, ensure_ascii=False, indent=4)
            f.close()
            print("Sample data written to file.")

        # Step 1: Collect all candidate URLs (or other unique keys)
        candidate_urls = [dotdict(a).url for a in article_data]

        candidate_authors = [dotdict(a).author_id for a in article_data]

        # Step 3: Filter out duplicates in Python
        new_articles = []

        for a in article_data:
            a["id"] = uuid.uuid4()
            new_articles.append(dotdict(a))

        press_name_map = {
            article.press_id: article.press_name
            for article in new_articles
        }

        press_name_map["000"] = "Unknown"

        new_authors = set([
            (author.author_name, author.author_id, author.press_id) for author in new_articles if author.press_id in press_name_map.keys()
        ])

        article_press = [a.press_id for a in new_articles]

        new_press = set([
            (press_id, press_name, press_logo) for press_id, press_name, press_logo in press_logo_set if press_id in article_press
        ])
        
        print("Inserting press")

        # print(list(new_press))

        session.add_all(
            Press(
                id=press_id,
                logo_img_src=press_logo,
                name=press_name
            ) for press_id, press_name, press_logo in new_press
        )

        print("Complete! \nInserting authors")
        session.add_all(
            Author(
                name=author[0],
                id=str(author[1])+str(author[2]),
                author_key=author[1],
                press_id=author[2]
            ) for author in new_authors
        )
        print(new_articles[0])

        print("Complete! \nInserting articles")
        session.add_all(
            Article(
                id=a.id,
                title=a.title,
                url=a.url,
                content=a.content,
                published_at=a.published_at,
                edited_at=a.edited_at,
                genre=a.genre,
                activity_score=a.activity_score,
                ranking=a.ranking,
                author_id=str(a.author_id)+str(a.press_id),
                press_id=a.press_id,
                story_summary=None
            ) for a in new_articles
        )


        print("Complete!\n Flushing...")
        session.flush()
        session.commit()

        print("Complete!")

    except Exception as e:
        print(f"Error during crawling: {e}")
        exit(-1)
    
if session:
    try:
        session.close()
    except Exception as e:
        print(f"Error closing session: {e}")
