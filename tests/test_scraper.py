import pytest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from app.scraper.utils import clean_text, extract_year, extract_citation_count, build_search_url
from app.scraper.scholar_scraper import GoogleScholarScraper

def test_clean_text():
    """텍스트 정리 함수 테스트"""
    assert clean_text("  Test   Text  ") == "Test Text"
    assert clean_text("") == ""
    assert clean_text(None) == ""

def test_extract_year():
    """연도 추출 함수 테스트"""
    assert extract_year("Paper published in 2020") == 2020
    assert extract_year("2019 - Journal") == 2019
    assert extract_year("No year here") is None
    assert extract_year("") is None

def test_extract_citation_count():
    """인용 수 추출 함수 테스트"""
    assert extract_citation_count("Cited by 42") == 42
    assert extract_citation_count("42 citations") == 42
    assert extract_citation_count("No citations") == 0
    assert extract_citation_count("") == 0

def test_build_search_url():
    """검색 URL 생성 함수 테스트"""
    url = build_search_url("machine learning")
    assert "q=machine+learning" in url
    assert "start=0" in url
    
    url_with_start = build_search_url("AI", start=10)
    assert "q=AI" in url_with_start
    assert "start=10" in url_with_start
    
    url_with_date = build_search_url("python", sort_by_date=True)
    assert "scisbd=1" in url_with_date

@pytest.mark.parametrize("html,expected_title,expected_citations", [
    ("""
    <div class="gs_r gs_or gs_scl">
        <div class="gs_rt"><a href="http://example.com">Test Paper</a></div>
        <div class="gs_a">Author - Journal, 2020</div>
        <div class="gs_rs">This is abstract</div>
        <a>Cited by 42</a>
    </div>
    """, "Test Paper", 42),
    ("""
    <div class="gs_r gs_or gs_scl">
        <div class="gs_rt"><a href="http://example.com">Another Paper</a></div>
        <div class="gs_a">Author - Journal, 2019</div>
        <div class="gs_rs">This is abstract</div>
    </div>
    """, "Another Paper", 0),
])
def test_parse_paper_item(html, expected_title, expected_citations):
    """논문 항목 파싱 함수 테스트"""
    soup = BeautifulSoup(html, 'html.parser')
    paper_item = soup.select_one('div.gs_r.gs_or.gs_scl')
    
    scraper = GoogleScholarScraper()
    result = scraper._parse_paper_item(paper_item)
    
    assert result is not None
    assert result['title'] == expected_title
    assert result['citation_count'] == expected_citations

@patch('app.scraper.browser.browser_manager.get_browser')
def test_check_captcha(mock_get_browser):
    """CAPTCHA 확인 함수 테스트"""
    mock_browser = MagicMock()
    mock_get_browser.return_value = mock_browser
    
    # CAPTCHA 있는 경우
    mock_browser.find_elements.return_value = [MagicMock()]
    scraper = GoogleScholarScraper()
    assert scraper._check_captcha(mock_browser) is True
    
    # CAPTCHA 없는 경우
    mock_browser.find_elements.return_value = []
    assert scraper._check_captcha(mock_browser) is False 