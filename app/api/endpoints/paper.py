from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.paper import Paper, SearchParams, SearchResult
from app.services.paper_service import paper_service

router = APIRouter()

@router.post("/search", response_model=SearchResult, summary="논문 검색", description="Google Scholar에서 논문을 검색하고 인용 수 기준으로 정렬")
async def search_papers(
    params: SearchParams,
    db: Session = Depends(get_db)
):
    """
    Google Scholar에서 논문을 검색하고 인용 수 기준으로 정렬합니다.
    
    - **keyword**: 검색 키워드 (필수)
    - **sort_by_citations**: 인용 수 기준 정렬 여부 (기본값: True)
    - **year_from**: 검색 시작 연도 (선택)
    - **year_to**: 검색 종료 연도 (선택)
    - **min_citations**: 최소 인용 수 (선택)
    - **max_results**: 최대 결과 수 (기본값: 100)
    - **authors**: 저자 필터링 목록 (선택)
    """
    return await paper_service.search_papers(db, params)

@router.get("/", response_model=List[Paper], summary="논문 목록 조회", description="DB에 저장된 모든 논문 목록 조회")
def get_papers(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=500, description="반환할 최대 항목 수"),
    db: Session = Depends(get_db)
):
    """
    DB에 저장된 모든 논문 목록을 조회합니다.
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 반환할 최대 항목 수 (기본값: 100, 최대: 500)
    """
    return paper_service.get_papers(db, skip=skip, limit=limit)

@router.get("/most-cited", response_model=List[Paper], summary="인용 수 기준 상위 논문", description="인용 수 기준 상위 논문 목록 조회")
def get_most_cited_papers(
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 항목 수"),
    db: Session = Depends(get_db)
):
    """
    인용 수 기준으로 상위 논문 목록을 조회합니다.
    
    - **limit**: 반환할 최대 항목 수 (기본값: 10, 최대: 100)
    """
    return paper_service.get_most_cited_papers(db, limit=limit)

@router.get("/{paper_id}", response_model=Paper, summary="논문 세부 정보", description="특정 논문의 세부 정보 조회")
def get_paper(
    paper_id: int = Path(..., ge=1, description="논문 ID"),
    db: Session = Depends(get_db)
):
    """
    ID로 특정 논문의 세부 정보를 조회합니다.
    
    - **paper_id**: 논문의 ID (필수)
    """
    paper = paper_service.get_paper_by_id(db, paper_id)
    if paper is None:
        raise HTTPException(status_code=404, detail="논문을 찾을 수 없습니다")
    return paper 