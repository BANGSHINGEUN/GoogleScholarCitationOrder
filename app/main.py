import os
import time
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import init_logging
from app.db.base import Base, engine
from app.db.session import get_db
from app.api.endpoints import paper

# 로깅 초기화
logger = init_logging()

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI(
    title="Google Scholar Citation Order API",
    description="Google Scholar에서 논문을 인용 수(Citation) 순으로 검색하고 정렬하는 API",
    version="1.0.0",
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 서비스에서는 특정 도메인으로 제한하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 요청 처리 시간 로깅 미들웨어
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.debug(f"요청 처리 시간: {process_time:.4f}초 - {request.method} {request.url.path}")
    return response

# 라우터 등록
app.include_router(paper.router, prefix="/api/papers", tags=["논문 검색"])

# API 상태 체크 엔드포인트
@app.get("/", tags=["상태"])
def read_root():
    return {
        "status": "online",
        "api_version": "1.0.0",
        "docs_url": "/docs",
    }

# 서버 정보 엔드포인트
@app.get("/info", tags=["상태"])
def get_info(db: Session = Depends(get_db)):
    """서버 정보 및 DB 연결 상태를 반환합니다."""
    try:
        # DB 연결 테스트
        db.execute("SELECT 1").fetchall()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api_version": "1.0.0",
        "environment": os.environ.get("ENV", "development"),
        "database_status": db_status,
    }

# 앱 구동 이벤트
@app.on_event("startup")
async def startup_event():
    logger.info("애플리케이션이 시작되었습니다")

# 앱 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("애플리케이션이 종료됩니다")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
    ) 