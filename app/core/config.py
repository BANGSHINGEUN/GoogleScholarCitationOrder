import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API 설정
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    
    # 데이터베이스 설정
    DATABASE_URL: str = "sqlite:///./scholar.db"
    
    # Google Scholar 설정
    GOOGLE_SCHOLAR_URL: str = "https://scholar.google.com"
    SEARCH_DELAY: int = 5  # 검색 요청 간 지연 시간 (초)
    MAX_PAGE_COUNT: int = 100  # 최대 페이지 수
    USER_AGENT_ROTATION: bool = True  # User-Agent 회전 사용 여부
    
    # 브라우저 설정
    HEADLESS: bool = True  # 헤드리스 모드 여부 (화면 표시 없음)
    BROWSER_TYPE: str = "chrome"  # 브라우저 유형 (chrome, firefox 등)
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/scholar.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 