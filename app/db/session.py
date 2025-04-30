from .base import SessionLocal

def get_db():
    """데이터베이스 세션을 반환하는 유틸리티 함수
    
    FastAPI의 dependency injection 시스템과 함께 사용하기 위한 함수
    with 블록으로 자동 정리 기능 제공
    
    Yields:
        Session: SQLAlchemy 세션 객체
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 