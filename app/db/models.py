from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

# 논문과 저자의 다대다 관계를 위한 연결 테이블
paper_author = Table(
    "paper_author",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)

class Paper(Base):
    """Google Scholar 논문 정보 모델"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    url = Column(String(1000), nullable=True)
    pdf_url = Column(String(1000), nullable=True)
    citation_count = Column(Integer, default=0)
    publication_year = Column(Integer, nullable=True)
    venue = Column(String(500), nullable=True)  # 발행처 (저널/학술대회 등)
    
    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 정의
    authors = relationship("Author", secondary=paper_author, back_populates="papers")
    keywords = relationship("Keyword", back_populates="paper")
    
    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title[:50]}...', citation_count={self.citation_count})>"


class Author(Base):
    """논문 저자 모델"""
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    profile_url = Column(String(1000), nullable=True)
    
    # 관계 정의
    papers = relationship("Paper", secondary=paper_author, back_populates="authors")
    
    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"


class Keyword(Base):
    """논문 키워드 모델"""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), nullable=False)
    
    # 관계 정의
    paper = relationship("Paper", back_populates="keywords")
    
    def __repr__(self):
        return f"<Keyword(id={self.id}, word='{self.word}')>"


class SearchQuery(Base):
    """검색 쿼리 히스토리 모델"""
    __tablename__ = "search_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(500), nullable=False, index=True)
    filter_params = Column(Text, nullable=True)  # JSON 형식으로 저장된 필터 파라미터
    result_count = Column(Integer, default=0)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<SearchQuery(id={self.id}, query='{self.query}', result_count={self.result_count})>" 