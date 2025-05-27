from fastapi import FastAPI
from app.api.main import api_router
from fastapi.middleware.cors import CORSMiddleware


try:
    app = FastAPI(
        title="VEWS",
        description="쉬운 한국어 뉴스, 뷰스",
        version="1.0.0",
    )

    # 허용할 origin 목록
    origins = [
        "*",  # 개발 중이라면 전체 허용
        # "http://localhost:3000",
        # "https://yourfrontend.com",
    ]

    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,              # or ["*"]
        allow_credentials=True,
        allow_methods=["*"],                # GET, POST, OPTIONS, etc.
        allow_headers=["*"],                # Accept, Content-Type, etc.
    )


    @app.get("/")
    async def root():   
        return {"message": "Hello World"}


    app.include_router(api_router)
except Exception as e:
    print(f"Error initializing FastAPI app: {e}")
    raise