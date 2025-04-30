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

## 사용 방법

### 간편 검색 스크립트 사용 (Docker)

제공된 스크립트를 사용하여 간편하게 Google Scholar 검색을 실행할 수 있습니다:

```bash
./scholar_search.sh -k "검색어" -n 10 -o results.json
```

### Docker Compose를 사용한 검색

Docker Compose를 사용한 검색 스크립트도 제공됩니다:

```bash
./search_with_compose.sh -k "검색어" -n 10 -o results.json
```

#### 옵션

- `-k, --keyword KEYWORD` : 검색 키워드 (필수)
- `-n, --results NUMBER` : 결과 개수 (기본값: 10)
- `-f, --year-from YEAR` : 검색 시작 연도
- `-t, --year-to YEAR` : 검색 종료 연도
- `-c, --min-citations NUM` : 최소 인용 수
- `-o, --output FILENAME` : 결과 저장 파일명 (.json 또는 .csv)
- `-d, --sort-by-date` : 날짜순 정렬 (기본: 인용 수)
- `-h, --help` : 도움말 표시

### Docker 직접 실행

Docker 이미지를 직접 실행할 수도 있습니다:

```bash
# Docker 이미지 빌드
docker build -t google-scholar-scraper .

# 컨테이너 실행
docker run -it --rm -v $(pwd)/output:/app/output google-scholar-scraper --keyword "machine learning" --results 10 --output /app/output/results.json
```

### API 서버 실행

REST API 서버를 실행하려면 docker-compose를 사용합니다:

```bash
# API 서버 실행
docker-compose up -d
```

API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다.

자세한 API 사용 방법은 [USAGE.md](USAGE.md) 파일을 참조하세요.

## 설치 (로컬 개발)

로컬에서 개발하려면 다음 단계를 따르세요:

1. 저장소 클론:
   ```bash
   git clone https://github.com/yourusername/GoogleScholarCitationOrder.git
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
   MAX_PAGE_COUNT=10
   USER_AGENT_ROTATION=true
   HEADLESS=true
   ```

5. 서버 실행:
   ```bash
   uvicorn app.main:app --reload
   ```

## 직접 실행 (CLI)

CLI 도구를 사용하여 직접 검색할 수 있습니다:

```bash
python run_search.py --keyword "machine learning" --results 20 --output results.json
```

## 참고사항

- Google Scholar는 자동화된 검색을 감지하면 CAPTCHA를 요구할 수 있습니다.
- 많은 요청을 짧은 시간에 보내면 IP가 일시적으로 차단될 수 있습니다.
- SEARCH_DELAY 환경 변수를 조정하여 요청 간 지연 시간을 설정할 수 있습니다.
- MAX_PAGE_COUNT 환경 변수를 조정하여 스크랩할 최대 페이지 수를 설정할 수 있습니다.

## 라이선스

MIT License 