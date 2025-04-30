from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

# 기본 스키마 클래스들

class KeywordBase(BaseModel):
    word: str

class KeywordCreate(KeywordBase):
    pass

class Keyword(KeywordBase):
    id: int
    paper_id: int
    
    class Config:
        orm_mode = True


class AuthorBase(BaseModel):
    name: str
    profile_url: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int
    
    class Config:
        orm_mode = True


class PaperBase(BaseModel):
    title: str = Field(..., description="논문 제목")
    abstract: Optional[str] = Field(None, description="논문 초록")
    url: Optional[str] = Field(None, description="논문 URL")
    pdf_url: Optional[str] = Field(None, description="PDF 다운로드 URL")
    citation_count: int = Field(0, description="인용 수", ge=0)
    publication_year: Optional[int] = Field(None, description="출판 연도")
    venue: Optional[str] = Field(None, description="출판 저널/학회")

class PaperCreate(PaperBase):
    authors: List[AuthorCreate] = Field([], description="논문 저자 목록")
    keywords: List[str] = Field([], description="논문 키워드 목록")

class Paper(PaperBase):
    id: int
    created_at: datetime
    updated_at: datetime
    authors: List[Author] = []
    keywords: List[Keyword] = []

    class Config:
        orm_mode = True


# 검색 관련 스키마

class SearchParams(BaseModel):
    """검색 파라미터 스키마"""
    keyword: str = Field(..., description="검색 키워드", min_length=1)
    sort_by_citations: bool = Field(True, description="인용 수 기준 정렬 여부")
    year_from: Optional[int] = Field(None, description="검색 시작 연도")
    year_to: Optional[int] = Field(None, description="검색 종료 연도")
    min_citations: Optional[int] = Field(None, description="최소 인용 수", ge=0)
    max_results: Optional[int] = Field(100, description="최대 결과 수", ge=1, le=1000)
    authors: Optional[List[str]] = Field(None, description="저자 필터링")

class SearchResult(BaseModel):
    """검색 결과 스키마"""
    query: str
    total_results: int
    papers: List[Paper]
    execution_time: float  # 실행 시간 (초) 