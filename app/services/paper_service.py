import json
import time
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import pandas as pd

from app.core.logging import logger
from app.schemas.paper import PaperCreate, Paper, SearchParams, SearchResult
from app.db.models import Paper as PaperModel, Author as AuthorModel, Keyword as KeywordModel, SearchQuery
from app.scraper.scholar_scraper import scholar_scraper

class PaperService:
    """논문 관련 서비스 로직"""
    
    async def search_papers(self, db: Session, params: SearchParams) -> SearchResult:
        """Google Scholar에서 논문 검색 및 결과 저장"""
        start_time = time.time()
        logger.info(f"논문 검색 서비스 요청: 키워드='{params.keyword}', 최대결과={params.max_results}")
        
        # 검색 실행
        paper_data = scholar_scraper.search(
            keyword=params.keyword,
            max_results=params.max_results,
            year_from=params.year_from,
            year_to=params.year_to,
            sort_by_date=not params.sort_by_citations  # sort_by_citations가 False면 날짜순 정렬
        )
        
        # 결과 필터링 (인용 수 필터)
        if params.min_citations is not None:
            paper_data = [p for p in paper_data if p.get('citation_count', 0) >= params.min_citations]
        
        # 저자 필터링
        if params.authors:
            filtered_papers = []
            for paper in paper_data:
                paper_authors = [a.get('name', '').lower() for a in paper.get('authors', [])]
                if any(author.lower() in paper_authors for author in params.authors):
                    filtered_papers.append(paper)
            paper_data = filtered_papers
        
        # 인용 수 기준 재정렬
        if params.sort_by_citations:
            paper_data = sorted(paper_data, key=lambda x: x.get('citation_count', 0), reverse=True)
        
        # 검색 기록 저장
        search_query = SearchQuery(
            query=params.keyword,
            filter_params=json.dumps({
                'year_from': params.year_from,
                'year_to': params.year_to,
                'min_citations': params.min_citations,
                'sort_by_citations': params.sort_by_citations,
                'authors': params.authors,
            }),
            result_count=len(paper_data),
        )
        db.add(search_query)
        db.commit()
        
        # 논문 DB 저장 (중복 확인 후)
        saved_papers = []
        for paper_dict in paper_data:
            paper_obj = self._save_paper(db, paper_dict)
            if paper_obj:
                saved_papers.append(paper_obj)
        
        # 응답 생성
        execution_time = time.time() - start_time
        result = SearchResult(
            query=params.keyword,
            total_results=len(saved_papers),
            papers=saved_papers,
            execution_time=execution_time
        )
        
        logger.info(f"검색 완료: {len(saved_papers)}개 결과, 소요 시간: {execution_time:.2f}초")
        return result

    def get_paper_by_id(self, db: Session, paper_id: int) -> Optional[Paper]:
        """ID로 논문 조회"""
        db_paper = db.query(PaperModel).filter(PaperModel.id == paper_id).first()
        if db_paper is None:
            return None
        return Paper.from_orm(db_paper)
    
    def get_papers(self, db: Session, skip: int = 0, limit: int = 100) -> List[Paper]:
        """논문 목록 조회"""
        db_papers = db.query(PaperModel).offset(skip).limit(limit).all()
        return [Paper.from_orm(paper) for paper in db_papers]
    
    def get_most_cited_papers(self, db: Session, limit: int = 10) -> List[Paper]:
        """인용 수 기준 상위 논문 조회"""
        db_papers = db.query(PaperModel).order_by(PaperModel.citation_count.desc()).limit(limit).all()
        return [Paper.from_orm(paper) for paper in db_papers]
    
    def export_papers_to_csv(self, db: Session, file_path: str) -> bool:
        """논문 데이터를 CSV 파일로 내보내기"""
        try:
            # 논문 데이터 조회
            papers = db.query(PaperModel).all()
            
            # 데이터프레임 변환
            data = []
            for paper in papers:
                authors = ', '.join([author.name for author in paper.authors])
                keywords = ', '.join([kw.word for kw in paper.keywords])
                
                data.append({
                    'id': paper.id,
                    'title': paper.title,
                    'authors': authors,
                    'year': paper.publication_year,
                    'venue': paper.venue,
                    'citation_count': paper.citation_count,
                    'keywords': keywords,
                    'url': paper.url,
                    'pdf_url': paper.pdf_url,
                })
            
            # CSV 저장
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False, encoding='utf-8')
            logger.info(f"{len(data)}개 논문 데이터를 {file_path}에 저장했습니다.")
            return True
            
        except Exception as e:
            logger.error(f"CSV 내보내기 중 오류 발생: {str(e)}")
            return False
    
    def _save_paper(self, db: Session, paper_dict: Dict[str, Any]) -> Optional[Paper]:
        """논문 정보를 DB에 저장 (중복 확인)"""
        try:
            # 제목으로 중복 확인
            existing_paper = db.query(PaperModel).filter(PaperModel.title == paper_dict['title']).first()
            
            # 기존 논문이 있으면 인용 수 업데이트
            if existing_paper:
                if existing_paper.citation_count != paper_dict['citation_count']:
                    existing_paper.citation_count = paper_dict['citation_count']
                    existing_paper.updated_at = time.time()
                    db.commit()
                return Paper.from_orm(existing_paper)
            
            # 새 논문 모델 생성
            new_paper = PaperModel(
                title=paper_dict['title'],
                abstract=paper_dict.get('abstract'),
                url=paper_dict.get('url'),
                pdf_url=paper_dict.get('pdf_url'),
                citation_count=paper_dict.get('citation_count', 0),
                publication_year=paper_dict.get('publication_year'),
                venue=paper_dict.get('venue')
            )
            db.add(new_paper)
            db.flush()  # ID 생성을 위한 flush
            
            # 저자 정보 저장
            for author_data in paper_dict.get('authors', []):
                # 기존 저자 확인
                author_name = author_data['name']
                existing_author = db.query(AuthorModel).filter(AuthorModel.name == author_name).first()
                
                if existing_author:
                    author = existing_author
                else:
                    # 새 저자 생성
                    author = AuthorModel(
                        name=author_name,
                        profile_url=author_data.get('profile_url')
                    )
                    db.add(author)
                    db.flush()
                
                # 논문-저자 관계 설정
                new_paper.authors.append(author)
            
            # 키워드 저장 (추출한 경우)
            for keyword in paper_dict.get('keywords', []):
                new_keyword = KeywordModel(word=keyword, paper_id=new_paper.id)
                db.add(new_keyword)
            
            db.commit()
            return Paper.from_orm(new_paper)
            
        except Exception as e:
            db.rollback()
            logger.error(f"논문 저장 중 오류 발생: {str(e)}")
            return None

# 서비스 인스턴스 생성
paper_service = PaperService() 