import time
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from app.core.config import settings
from app.core.logging import logger
from app.schemas.paper import PaperCreate, AuthorCreate
from .browser import browser_manager
from .utils import clean_text, extract_year, extract_citation_count, build_search_url

class GoogleScholarScraper:
    """Google Scholar 크롤링 클래스"""
    
    def __init__(self):
        self.browser_manager = browser_manager
        self.base_url = settings.GOOGLE_SCHOLAR_URL
    
    def search(self, keyword: str, max_results: int = 100, year_from: Optional[int] = None, 
               year_to: Optional[int] = None, sort_by_date: bool = False, 
               max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """Google Scholar 검색 수행
        
        Args:
            keyword: 검색 키워드
            max_results: 최대 검색 결과 수
            year_from: 검색 시작 연도
            year_to: 검색 종료 연도
            sort_by_date: 날짜순 정렬 여부
            max_pages: 최대 검색 페이지 수 (None이면 설정 값 사용)
            
        Returns:
            List[Dict[str, Any]]: 검색 결과 목록
        """
        start_time = time.time()
        logger.info(f"검색 시작: '{keyword}', 최대 결과 수: {max_results}")
        logger.info(f"연도 필터: {year_from} - {year_to}")
        
        try:
            browser = self.browser_manager.get_browser()
            all_papers = []
            page = 0
            results_per_page = 10
            
            # 날짜 필터 추가된 검색 쿼리
            search_query = keyword
            if year_from or year_to:
                date_filter = ""
                if year_from:
                    # 정확히 시작 연도부터 검색하기 위해 year_from 자체를 사용
                    date_filter += f" after:{year_from-1}"
                if year_to:
                    # 정확히 종료 연도까지 검색하기 위해 year_to 자체를 사용
                    date_filter += f" before:{year_to+1}"
                search_query = f"{keyword}{date_filter}"
                logger.info(f"검색 쿼리 (날짜 필터 포함): '{search_query}'")
            
            # 최대 페이지 수 설정 - 사용자 지정 또는 기본 설정 사용
            pages_to_search = max_pages if max_pages is not None else settings.MAX_PAGE_COUNT
            logger.info(f"설정된 최대 페이지 수: {pages_to_search} (모든 가능한 결과를 수집 후 정렬)")
            
            empty_page_count = 0  # 연속으로 빈 페이지 카운트
            timeout_count = 0     # 연속 타임아웃 횟수
            
            # 수정: max_results에 상관없이 지정된 max_pages까지 모든 페이지 탐색
            while page < pages_to_search:
                # 검색 URL 생성 및 요청
                start_idx = page * results_per_page
                search_url = build_search_url(search_query, start_idx, sort_by_date)
                logger.debug(f"페이지 {page+1} 요청: {search_url}")
                
                # 브라우저로 페이지 로드
                browser.get(search_url)
                
                # 검색 지연 시간을 늘려 IP 차단 방지
                # 현재 페이지에 따라 지연 시간 점진적 증가
                delay_factor = min(1 + (page // 10) * 0.5, 3)  # 페이지가 많을수록 대기 시간 증가 (최대 3배)
                delay_min = settings.SEARCH_DELAY * delay_factor
                delay_max = delay_min + 2
                self.browser_manager.random_delay(delay_min, delay_max)
                
                # 캡챠 확인
                if self._check_captcha(browser):
                    logger.warning("CAPTCHA 감지됨. 검색 중단.")
                    break
                
                # 페이지 파싱
                retry_count = 0
                max_retries = 3
                timeout_value = 20  # 타임아웃 값 증가 (초)
                
                while retry_count < max_retries:
                    try:
                        # 타임아웃 값 증가
                        WebDriverWait(browser, timeout_value).until(
                            EC.presence_of_element_located((By.ID, "gs_res_ccl"))
                        )
                        
                        # 성공하면 타임아웃 카운트 초기화
                        timeout_count = 0
                        
                        # 페이지 내용 파싱
                        page_source = browser.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')
                        
                        # 논문 항목 추출
                        paper_items = soup.select('div.gs_r.gs_or.gs_scl')
                        
                        if not paper_items:
                            logger.debug(f"결과 없음 (페이지 {page+1})")
                            empty_page_count += 1
                            
                            # 연속으로 3번 빈 페이지가 나오면 종료 (Google이 더 이상 결과를 제공하지 않음)
                            if empty_page_count >= 3:
                                logger.info("연속 3번 빈 페이지 발생. 더 이상 결과가 없는 것으로 판단하여 검색 종료")
                                break
                            
                            page += 1
                            break  # 재시도 루프 종료
                        else:
                            # 결과가 있으면 빈 페이지 카운트 초기화
                            empty_page_count = 0
                        
                        # 각 논문 정보 추출
                        for item in paper_items:
                            paper_data = self._parse_paper_item(item)
                            if paper_data:
                                # 논문 연도 필터링 추가 검증
                                paper_year = paper_data.get('publication_year')
                                year_match = True
                                
                                # 추가 필터링: 스크래핑된 결과도 연도 조건을 적용
                                if paper_year and year_from and paper_year < year_from:
                                    year_match = False
                                    logger.debug(f"연도 필터 미달: {paper_data['title']} ({paper_year} < {year_from})")
                                
                                if paper_year and year_to and paper_year > year_to:
                                    year_match = False
                                    logger.debug(f"연도 필터 초과: {paper_data['title']} ({paper_year} > {year_to})")
                                
                                # 필터링 통과한 논문만 추가
                                if year_match:
                                    # 중복 검사 (제목 기준)
                                    if not any(p['title'] == paper_data['title'] for p in all_papers):
                                        all_papers.append(paper_data)
                                        logger.debug(f"추출된 논문: {paper_data['title'][:50]}... (인용 수: {paper_data['citation_count']}, 연도: {paper_year})")
                        
                        # 진행 상황 출력
                        if page % 5 == 0:
                            logger.info(f"현재까지 {len(all_papers)}개 논문 추출됨 (페이지 {page+1})")
                        
                        # User-Agent 회전 (설정된 경우)
                        if settings.USER_AGENT_ROTATION:
                            self.browser_manager.rotate_user_agent()
                        
                        page += 1
                        break  # 성공적으로 페이지를 파싱했으므로 재시도 루프 종료
                        
                    except TimeoutException:
                        retry_count += 1
                        timeout_count += 1
                        
                        if retry_count >= max_retries:
                            logger.error(f"페이지 로딩 타임아웃 (최대 재시도 횟수 초과): 페이지 {page+1}")
                            
                            # 여러 번 연속으로 타임아웃이 발생하면 검색 종료
                            if timeout_count >= 5:
                                logger.error("연속 5번 타임아웃 발생. Google Scholar에서 차단된 것으로 판단하여 검색 종료")
                                return all_papers  # 현재까지 수집된 결과 반환
                            
                            # 타임아웃 후에도 다음 페이지로 이동 시도
                            page += 1
                            break
                        
                        # 지수 백오프 적용 (재시도 간 대기 시간 증가)
                        backoff_time = (2 ** retry_count) * random.uniform(5, 10)
                        logger.warning(f"페이지 {page+1} 로딩 타임아웃, {retry_count}/{max_retries} 재시도 중... {backoff_time:.1f}초 후 다시 시도")
                        time.sleep(backoff_time)
                        
                        # 재시도 시 새로운 User-Agent 사용
                        if settings.USER_AGENT_ROTATION:
                            self.browser_manager.rotate_user_agent()
                            
                    except Exception as e:
                        logger.error(f"검색 중 오류 발생: {str(e)}")
                        page += 1
                        break
            
            logger.info(f"검색 완료: 총 {len(all_papers)}개 논문 수집됨")
            
            # 결과 정렬 (인용 수 기준)
            logger.info("논문을 인용 수 기준으로 정렬 중...")
            sorted_papers = sorted(all_papers, key=lambda x: x.get('citation_count', 0), reverse=True)
            
            # 사용자가 요청한 최대 결과 수 이하로 자르기
            result_papers = sorted_papers
            if max_results > 0 and len(sorted_papers) > max_results:
                logger.info(f"상위 {max_results}개 논문만 결과로 반환")
                result_papers = sorted_papers[:max_results]
            
            execution_time = time.time() - start_time
            logger.info(f"전체 과정 완료: 총 {len(all_papers)}개 수집, {len(result_papers)}개 결과 반환, 소요 시간: {execution_time:.2f}초")
            
            return result_papers
            
        except Exception as e:
            logger.error(f"검색 실패: {str(e)}")
            return []
        finally:
            # 브라우저 인스턴스는 유지 (API에서 재사용)
            pass
    
    def _parse_paper_item(self, item) -> Optional[Dict[str, Any]]:
        """Google Scholar 검색 결과 항목에서 논문 정보 추출"""
        try:
            # 제목 추출
            title_element = item.select_one('.gs_rt a')
            if not title_element:
                return None
            
            title = clean_text(title_element.get_text())
            url = title_element.get('href', '')
            
            # 저자, 발행처, 연도 정보
            pub_info = item.select_one('.gs_a')
            authors = []
            venue = ""
            year = None
            
            if pub_info:
                pub_text = clean_text(pub_info.get_text())
                
                # 저자 추출 (첫 번째 '-' 이전의 텍스트)
                author_part = pub_text.split('-')[0] if '-' in pub_text else pub_text
                author_names = [clean_text(a) for a in author_part.split(',')]
                authors = [{'name': name, 'profile_url': None} for name in author_names if name]
                
                # 발행처 추출 (두 번째 '-' 부분)
                venue_parts = pub_text.split('-')
                if len(venue_parts) > 1:
                    venue = clean_text(venue_parts[1])
                
                # 연도 추출
                year = extract_year(pub_text)
            
            # 초록 추출
            abstract_element = item.select_one('.gs_rs')
            abstract = clean_text(abstract_element.get_text()) if abstract_element else ""
            
            # 인용 수 추출
            citation_element = item.select_one('a:contains("Cited by")')
            citation_count = 0
            if citation_element:
                citation_text = citation_element.get_text()
                citation_count = extract_citation_count(citation_text)
            
            # PDF 링크 추출
            pdf_link_element = item.select_one('.gs_or_ggsm a:contains("[PDF]")')
            pdf_url = pdf_link_element.get('href') if pdf_link_element else None
            
            return {
                'title': title,
                'url': url,
                'abstract': abstract,
                'authors': authors,
                'venue': venue,
                'publication_year': year,
                'citation_count': citation_count,
                'pdf_url': pdf_url
            }
            
        except Exception as e:
            logger.error(f"논문 항목 파싱 중 오류: {str(e)}")
            return None
    
    def _check_captcha(self, browser) -> bool:
        """CAPTCHA 페이지 확인"""
        try:
            captcha_elements = browser.find_elements(By.ID, "captcha-form")
            return len(captcha_elements) > 0
        except:
            return False
    
    def close(self):
        """리소스 정리"""
        self.browser_manager.close()


# 인스턴스 생성
scholar_scraper = GoogleScholarScraper()


# CLI 지원 (직접 실행하는 경우)
if __name__ == "__main__":
    import argparse
    import json
    
    # CLI 인자 파싱
    parser = argparse.ArgumentParser(description='Google Scholar 인용 수 기준 검색')
    parser.add_argument('--keyword', type=str, required=True, help='검색 키워드')
    parser.add_argument('--results', type=int, default=100, help='결과 수 (기본값: 100)')
    parser.add_argument('--year-from', type=int, help='검색 시작 연도')
    parser.add_argument('--year-to', type=int, help='검색 종료 연도')
    parser.add_argument('--sort-by-date', action='store_true', help='날짜순 정렬 (기본: 인용 수)')
    parser.add_argument('--output', type=str, help='결과 저장 파일 (.json 또는 .csv)')
    
    args = parser.parse_args()
    
    try:
        # 검색 실행
        scraper = GoogleScholarScraper()
        results = scraper.search(
            keyword=args.keyword,
            max_results=args.results,
            year_from=args.year_from,
            year_to=args.year_to,
            sort_by_date=args.sort_by_date
        )
        
        # 결과 출력
        print(f"\n검색 결과: {len(results)}개 논문\n")
        for i, paper in enumerate(results, 1):
            print(f"{i}. {paper['title']} (인용: {paper['citation_count']})")
            if paper['authors']:
                authors_str = ', '.join([a['name'] for a in paper['authors']])
                print(f"   저자: {authors_str}")
            if paper['publication_year']:
                print(f"   발행: {paper['publication_year']}")
            if paper['url']:
                print(f"   URL: {paper['url']}")
            print()
        
        # 결과 저장 (지정된 경우)
        if args.output:
            if args.output.endswith('.json'):
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"결과를 {args.output}에 저장했습니다.")
            elif args.output.endswith('.csv'):
                df = pd.DataFrame(results)
                df.to_csv(args.output, index=False, encoding='utf-8')
                print(f"결과를 {args.output}에 저장했습니다.")
            else:
                print("지원되지 않는 출력 형식입니다. .json 또는 .csv 확장자를 사용하세요.")
        
    except KeyboardInterrupt:
        print("\n검색이 중단되었습니다.")
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
    finally:
        # 리소스 정리
        scraper.close() 