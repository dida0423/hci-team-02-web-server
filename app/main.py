from fastapi import FastAPI
from app.api.main import api_router

try:
    app = FastAPI(
        title="VEWS",
        description="쉬운 한국어 뉴스, 뷰스",
        version="1.0.0",
    )


    @app.get("/")
    async def root():   
        return {"message": "Hello World"}


    app.include_router(api_router)
except Exception as e:
    print(f"Error initializing FastAPI app: {e}")
    raise