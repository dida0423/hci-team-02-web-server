from fastapi import APIRouter

from app.api.routes import article

# Set routes
api_router = APIRouter()
api_router.include_router(article.router)