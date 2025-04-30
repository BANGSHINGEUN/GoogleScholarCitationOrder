import re
from typing import Union, List, Dict, Any, Optional
from urllib.parse import quote_plus, urlparse, parse_qs

def clean_text(text: str) -> str:
    """텍스트 정리: 불필요한 공백 및 특수문자 제거"""
    if not text:
        return ""
    # 여러 공백을 하나로 변환하고 앞뒤 공백 제거
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_year(text: str) -> Optional[int]:
    """텍스트에서 연도 추출 (예: '2021', '… - ‎2019'에서 연도 추출)"""
    if not text:
        return None
    
    # 연도 패턴 검색 (4자리 숫자, 1900-2100 사이)
    year_match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    if year_match:
        return int(year_match.group(1))
    return None

def extract_citation_count(citation_text: str) -> int:
    """인용 수 텍스트에서 숫자만 추출 (예: 'Cited by 42'에서 42 추출)"""
    if not citation_text:
        return 0
    
    # 숫자만 추출
    numbers = re.findall(r'\d+', citation_text)
    if numbers:
        return int(numbers[0])
    return 0

def build_search_url(keyword: str, start: int = 0, sort_by_date: bool = False) -> str:
    """Google Scholar 검색 URL 생성
    
    Args:
        keyword: 검색 키워드
        start: 검색 결과 시작 인덱스 (페이지네이션용)
        sort_by_date: 날짜순 정렬 여부 (True: 날짜순, False: 관련성)
    
    Returns:
        str: 검색 URL
    """
    # 키워드 URL 인코딩
    encoded_keyword = quote_plus(keyword)
    
    # 기본 URL 생성
    base_url = f"https://scholar.google.com/scholar?q={encoded_keyword}&hl=en&start={start}"
    
    # 정렬 기준 추가
    if sort_by_date:
        base_url += "&scisbd=1"  # 날짜순 정렬
    
    return base_url

def extract_query_params(url: str) -> Dict[str, str]:
    """URL에서 쿼리 파라미터 추출"""
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    
    # 리스트 형태의 값들을 단일 값으로 변환
    return {k: v[0] if v and len(v) == 1 else v for k, v in params.items()} 