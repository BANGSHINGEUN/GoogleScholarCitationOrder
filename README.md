# Google Scholar Citation Order

Google Scholar에서 검색한 논문 결과를 인용 수(Citations) 기준으로 정렬하는 프로젝트입니다.

## 개요

Google Scholar는 기본적으로 검색 결과를 인용 수 기준으로 정렬하는 기능을 제공하지 않습니다. 이 프로젝트는 Google Scholar에서 논문을 검색하고, 검색 결과를 인용 수에 따라 정렬하여 보여주는 기능을 제공합니다.

## 기능

- Google Scholar 검색 자동화
- 검색 결과를 인용 수 기준으로 정렬
- 연도별 필터링 지원
- 최소 인용 수 필터링 지원
- 결과를 JSON 또는 CSV로 저장
- API 및 CLI 지원
- Docker 컨테이너화 지원

## 1. 간편 검색 스크립트 사용 (Docker)

제공된 스크립트를 사용하여 간편하게 Google Scholar 검색을 실행할 수 있습니다:

### 기본 사용법

```bash
./scholar_search.sh -k "검색어" -n 결과수 -p 페이지수 -o 출력파일명
```

### 예제

```bash
# 기본 검색 (키워드 "deep learning", 결과 10개)
./scholar_search.sh -k "deep learning"

# 20개 결과를 JSON 파일로 저장
./scholar_search.sh -k "machine learning" -n 20 -o results.json

# 최대 50페이지 크롤링하여 결과 검색 (약 500개 논문 중에서 상위 결과 선택)
./scholar_search.sh -k "neural networks" -p 50 -n 20

# 2020년 이후 논문만 검색
./scholar_search.sh -k "artificial intelligence" -f 2020

# 최소 인용 수 1000회 이상 논문 검색
./scholar_search.sh -k "computer vision" -c 1000

# 결과를 CSV 형식으로 저장
./scholar_search.sh -k "natural language processing" -o nlp_papers.csv

# 발행 날짜순 정렬
./scholar_search.sh -k "robotics" -d
```

## 2. Docker Compose를 사용한 검색

Docker Compose를 사용한 검색 스크립트도 제공됩니다:

### 기본 사용법

```bash
./search_with_compose.sh -k "검색어" -n 결과수 -p 페이지수 -o 출력파일명
```

### 예제

```bash
# 기본 검색 (키워드 "deep learning", 결과 10개)
./search_with_compose.sh -k "deep learning"

# 20개 결과를 JSON 파일로 저장, 최대 30페이지 검색
./search_with_compose.sh -k "machine learning" -n 20 -p 30 -o results.json

# 2020년 이후 논문만 검색
./search_with_compose.sh -k "artificial intelligence" -f 2020

# 최소 인용 수 1000회 이상 논문 검색
./search_with_compose.sh -k "computer vision" -c 1000

# 결과를 CSV 형식으로 저장
./search_with_compose.sh -k "natural language processing" -o nlp_papers.csv

# 발행 날짜순 정렬
./search_with_compose.sh -k "robotics" -d
```

### 옵션 설명

- `-k, --keyword KEYWORD` : 검색 키워드 (필수)
- `-n, --results NUMBER` : 반환할 결과 개수 (기본값: 10)
- `-f, --year-from YEAR` : 검색 시작 연도
- `-t, --year-to YEAR` : 검색 종료 연도
- `-c, --min-citations NUM` : 최소 인용 수
- `-o, --output FILENAME` : 결과 저장 파일명 (.json 또는 .csv)
- `-p, --max-pages NUM` : 크롤링할 최대 페이지 수 (기본값: 환경 설정값 사용, 일반적으로 100)
- `-d, --sort-by-date` : 날짜순 정렬 (기본: 인용 수)
- `-h, --help` : 도움말 표시

## 3. Docker 직접 실행

Docker 이미지를 직접 실행하여 더 세부적인 옵션을 지정할 수 있습니다:

### 기본 사용법

```bash
# Docker 이미지 빌드
docker build -t google-scholar-scraper .

# 컨테이너 실행
docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper [옵션]
```

### 예제

```bash
# 도움말 보기
docker run -it --rm google-scholar-scraper --help

# 검색 실행 및 결과 저장 (50페이지 크롤링 후 상위 30개 결과 반환)
docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper \
  --keyword "quantum computing" \
  --results 30 \
  --max-pages 50 \
  --year-from 2018 \
  --year-to 2023 \
  --min-citations 50 \
  --output /app/output/quantum_papers.json
```

## 4. Python API 직접 사용

프로젝트를 로컬에 설치한 경우, Python API를 직접 사용할 수 있습니다:

```python
from app.scraper.scholar_scraper import GoogleScholarScraper

# 스크래퍼 초기화
scraper = GoogleScholarScraper()

try:
    # 검색 실행 (최대 50페이지 크롤링 후 상위 20개 결과 반환)
    results = scraper.search(
        keyword="deep learning",
        max_results=20,
        year_from=2020,
        year_to=2023,
        sort_by_date=False,
        max_pages=50
    )
    
    # 결과 처리
    for paper in results:
        print(f"{paper['title']} (인용: {paper['citation_count']})")
        
finally:
    # 리소스 정리
    scraper.close()
```

## 5. REST API 사용

REST API 서버를 실행한 경우, HTTP 요청을 통해 서비스를 사용할 수 있습니다:

### API 서버 실행

```bash
docker-compose up -d
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

## 6. 설치 (로컬 개발)

로컬에서 개발하려면 다음 단계를 따르세요:

1. 저장소 클론:
   ```bash
   git clone https://github.com/BANGSHINGEUN/GoogleScholarCitationOrder.git
   cd GoogleScholarCitationOrder
   ```

2. 가상환경 생성 및 활성화:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```

4. 환경 변수 설정 (.env 파일 생성):
   ```
   DATABASE_URL=sqlite:///./scholar.db
   SEARCH_DELAY=2
   MAX_PAGE_COUNT=100
   USER_AGENT_ROTATION=true
   HEADLESS=true
   ```

5. 서버 실행:
   ```bash
   uvicorn app.main:app --reload
   ```

## 7. 직접 실행 (CLI)

CLI 도구를 사용하여 직접 검색할 수 있습니다:

```bash
python run_search.py --keyword "machine learning" --results 20 --max-pages 50 --output results.json
```

## 8. 환경 변수 설정

`.env` 파일을 통해 다양한 설정을 조정할 수 있습니다:

```
# 기본 설정
DATABASE_URL=sqlite:///./scholar.db
API_PORT=8000
API_HOST=0.0.0.0

# 검색 설정
GOOGLE_SCHOLAR_URL=https://scholar.google.com
SEARCH_DELAY=2
MAX_PAGE_COUNT=100
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

## 9. 페이지 수와 결과 수의 차이점

- `max_pages` (또는 `-p`): 구글 스칼라에서 크롤링할 최대 페이지 수입니다. 각 페이지에는 약 10개의 결과가 있으므로, 50페이지는 약 500개의 논문을 의미합니다. 이 옵션을 사용하면 도구는 지정된 페이지 수만큼 모든 결과를 검색한 후 인용 수를 기준으로 정렬합니다.

- `max_results` (또는 `-n`): 최종적으로 반환할 결과의 수입니다. 예를 들어, 50페이지(약 500개 논문)를 크롤링한 후 인용 수로 정렬하여 상위 20개만 반환하고 싶다면 `-p 50 -n 20`을 사용합니다.

## 10. 주의사항

- Google Scholar는 자동화된 검색을 감지하면 CAPTCHA를 요구할 수 있습니다.
- 많은 요청을 짧은 시간에 보내면 IP가 일시적으로 차단될 수 있습니다.
- 연구 및 개인 용도로만 사용하세요.
- Google의 서비스 약관을 준수하세요.

## 라이선스

MIT License 