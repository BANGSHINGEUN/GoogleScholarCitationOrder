import pytest
from fastapi.testclient import TestClient

def test_read_root(client):
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "online"

def test_read_info(client):
    """정보 엔드포인트 테스트"""
    response = client.get("/info")
    assert response.status_code == 200
    data = response.json()
    assert "api_version" in data
    assert "database_status" in data

def test_search_papers_validation(client):
    """논문 검색 유효성 검사 테스트"""
    # 빈 키워드 검증
    response = client.post("/api/papers/search", json={
        "keyword": "",
        "sort_by_citations": True,
        "max_results": 10
    })
    assert response.status_code == 422  # 유효성 검사 실패

    # 최대 결과 수 검증
    response = client.post("/api/papers/search", json={
        "keyword": "test",
        "sort_by_citations": True,
        "max_results": 1001  # 최대 값 초과
    })
    assert response.status_code == 422  # 유효성 검사 실패 