# Google Scholar Citation Order 사용 가이드

이 문서에서는 Google Scholar Citation Order 도구의 다양한 사용 방법을 설명합니다.

## 1. 간편 검색 스크립트 사용

`scholar_search.sh` 스크립트를 사용하면 Docker를 통해 쉽게 Google Scholar 검색을 수행할 수 있습니다.

### 기본 사용법

```bash
./scholar_search.sh -k "검색어" -n 결과수 -o 출력파일명
```

### 예제

```bash
# 기본 검색 (키워드 "deep learning", 결과 10개)
./scholar_search.sh -k "deep learning"

# 20개 결과를 JSON 파일로 저장
./scholar_search.sh -k "machine learning" -n 20 -o results.json

# 2020년 이후 논문만 검색
./scholar_search.sh -k "artificial intelligence" -f 2020

# 최소 인용 수 1000회 이상 논문 검색
./scholar_search.sh -k "computer vision" -c 1000

# 결과를 CSV 형식으로 저장
./scholar_search.sh -k "natural language processing" -o nlp_papers.csv

# 발행 날짜순 정렬
./scholar_search.sh -k "robotics" -d
```

## 1.1 Docker Compose를 사용한 검색

`search_with_compose.sh` 스크립트를 사용하면 Docker Compose를 통해 쉽게 Google Scholar 검색을 수행할 수 있습니다.

### 기본 사용법

```bash
./search_with_compose.sh -k "검색어" -n 결과수 -o 출력파일명
```

### 예제

```bash
# 기본 검색 (키워드 "deep learning", 결과 10개)
./search_with_compose.sh -k "deep learning"

# 20개 결과를 JSON 파일로 저장
./search_with_compose.sh -k "machine learning" -n 20 -o results.json

# 2020년 이후 논문만 검색
./search_with_compose.sh -k "artificial intelligence" -f 2020

# 최소 인용 수 1000회 이상 논문 검색
./search_with_compose.sh -k "computer vision" -c 1000

# 결과를 CSV 형식으로 저장
./search_with_compose.sh -k "natural language processing" -o nlp_papers.csv

# 발행 날짜순 정렬
./search_with_compose.sh -k "robotics" -d
```

## 2. Docker 직접 실행

Docker 이미지를 직접 실행하여 더 세부적인 옵션을 지정할 수 있습니다.

### 기본 사용법

```bash
docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper [옵션]
```

### 예제

```bash
# 도움말 보기
docker run -it --rm google-scholar-scraper --help

# 검색 실행 및 결과 저장
docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper \
  --keyword "quantum computing" \
  --results 30 \
  --year-from 2018 \
  --year-to 2023 \
  --min-citations 50 \
  --output /app/output/quantum_papers.json
```

## 3. Python API 직접 사용

프로젝트를 로컬에 설치한 경우, Python API를 직접 사용할 수 있습니다.

```python
from app.scraper.scholar_scraper import GoogleScholarScraper

# 스크래퍼 초기화
scraper = GoogleScholarScraper()

try:
    # 검색 실행
    results = scraper.search(
        keyword="deep learning",
        max_results=20,
        year_from=2020,
        year_to=2023,
        sort_by_date=False
    )
    
    # 결과 처리
    for paper in results:
        print(f"{paper['title']} (인용: {paper['citation_count']})")
        
finally:
    # 리소스 정리
    scraper.close()
```

## 4. REST API 사용

REST API 서버를 실행한 경우, HTTP 요청을 통해 서비스를 사용할 수 있습니다.

### API 서버 실행

```bash
docker compose up -d
```

### API 엔드포인트

API 서버는 다음 엔드포인트를 제공합니다:

- `GET /api/papers/search` - 논문 검색
- `GET /api/papers/{id}` - 특정 논문 조회
- `GET /api/papers/` - 저장된 논문 목록 조회

### 검색 API 사용 예제 (cURL)

```bash
# 기본 검색
curl -X GET "http://localhost:8000/api/papers/search?keyword=machine%20learning&max_results=10"

# 연도 필터링 적용
curl -X GET "http://localhost:8000/api/papers/search?keyword=artificial%20intelligence&year_from=2020&year_to=2023"

# 인용 횟수로 정렬
curl -X GET "http://localhost:8000/api/papers/search?keyword=deep%20learning&sort_by_date=false"
```

### 검색 API 사용 예제 (JavaScript)

```javascript
// 비동기 함수로 API 호출
async function searchPapers() {
  const response = await fetch(
    'http://localhost:8000/api/papers/search?keyword=machine%20learning&max_results=20'
  );
  const data = await response.json();
  console.log(data);
}

searchPapers();
```

## 5. 환경 변수 설정

`.env` 파일을 통해 다양한 설정을 조정할 수 있습니다:

```
# 기본 설정
DATABASE_URL=sqlite:///./scholar.db
API_PORT=8000
API_HOST=0.0.0.0

# 검색 설정
GOOGLE_SCHOLAR_URL=https://scholar.google.com
SEARCH_DELAY=2
MAX_PAGE_COUNT=10
USER_AGENT_ROTATION=true

# 브라우저 설정
HEADLESS=true
BROWSER_TYPE=chrome

# 로깅 설정
LOG_LEVEL=INFO
LOG_FILE=logs/scholar.log
```

### 주요 환경 변수 설명

- `SEARCH_DELAY`: 검색 요청 간 지연 시간(초). 값이 클수록 Google Scholar의 차단 가능성이 낮아지지만 검색 속도가 느려집니다.
- `MAX_PAGE_COUNT`: 검색할 최대 페이지 수. 값이 클수록 더 많은 논문을 스크랩할 수 있지만 시간이 오래 걸립니다.
- `HEADLESS`: 브라우저 화면 표시 여부. `false`로 설정하면 브라우저 창이 화면에 표시됩니다.
- `USER_AGENT_ROTATION`: User-Agent 회전 사용 여부. Google Scholar의 차단을 우회하는 데 도움이 됩니다.

## 6. 주의사항

- Google Scholar는 자동화된 검색을 감지하면 CAPTCHA를 요구할 수 있습니다.
- 많은 요청을 짧은 시간에 보내면 IP가 일시적으로 차단될 수 있습니다.
- 연구 및 개인 용도로만 사용하세요.
- Google의 서비스 약관을 준수하세요. 