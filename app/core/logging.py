import os
import sys
from loguru import logger
from .config import settings

# 로깅 설정 초기화
def init_logging():
    # 기존 로거 리셋
    logger.remove()
    
    # 로그 디렉토리 생성
    if settings.LOG_FILE:
        log_dir = os.path.dirname(settings.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    # 콘솔 로깅 설정
    logger.add(
        sys.stderr,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    
    # 파일 로깅 설정 (설정된 경우)
    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            rotation="10 MB",  # 로그 파일 크기가 10MB를 초과하면 새 파일 생성
            retention="1 month",  # 로그 파일 보관 기간
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            compression="zip",  # 순환된 로그 파일 압축
        )
    
    logger.info("로깅 시스템 초기화 완료")
    return logger 