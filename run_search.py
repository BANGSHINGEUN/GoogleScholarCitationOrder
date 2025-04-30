#!/usr/bin/env python
"""
Google Scholar Citation Order - CLI 검색 도구

이 스크립트는 Google Scholar에서 논문을 검색하고 인용 수 기준으로 결과를 정렬합니다.
"""

import argparse
import json
import time
import pandas as pd
from app.scraper.scholar_scraper import GoogleScholarScraper
from app.core.logging import init_logging

# 로깅 초기화
logger = init_logging()

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Google Scholar 인용 수 기준 검색 도구',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('--keyword', '-k', type=str, required=True, 
                        help='검색 키워드')
    parser.add_argument('--results', '-n', type=int, default=10, 
                        help='결과 수 (기본값: 10)')
    parser.add_argument('--year-from', type=int, 
                        help='검색 시작 연도')
    parser.add_argument('--year-to', type=int, 
                        help='검색 종료 연도')
    parser.add_argument('--min-citations', type=int, 
                        help='최소 인용 수')
    parser.add_argument('--output', '-o', type=str, 
                        help='결과 저장 파일 경로 (.json 또는 .csv)')
    parser.add_argument('--sort-by-date', action='store_true', 
                        help='날짜순 정렬 (기본: 인용 수)')
    parser.add_argument('--max-pages', '-p', type=int, default=None,
                        help='최대 검색 페이지 수 (기본값: 환경 설정 사용)')
    
    args = parser.parse_args()
    
    try:
        # 검색 실행
        scraper = GoogleScholarScraper()
        start_time = time.time()
        
        print(f"\n검색 중: '{args.keyword}'...")
        results = scraper.search(
            keyword=args.keyword,
            max_results=args.results,
            year_from=args.year_from,
            year_to=args.year_to,
            sort_by_date=args.sort_by_date,
            max_pages=args.max_pages
        )
        
        # 최소 인용 수 필터링
        if args.min_citations:
            results = [p for p in results if p.get('citation_count', 0) >= args.min_citations]
        
        # 인용 수 기준 정렬
        if not args.sort_by_date:
            results = sorted(results, key=lambda x: x.get('citation_count', 0), reverse=True)
        
        # 결과 출력
        execution_time = time.time() - start_time
        print(f"\n검색 결과: {len(results)}개 논문 (소요 시간: {execution_time:.2f}초)\n")
        
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
                # 중첩된 데이터 처리
                flat_data = []
                for paper in results:
                    paper_copy = paper.copy()
                    
                    # 저자 목록을 문자열로 변환
                    if 'authors' in paper_copy:
                        paper_copy['authors'] = ', '.join([a['name'] for a in paper_copy['authors']])
                    
                    flat_data.append(paper_copy)
                
                df = pd.DataFrame(flat_data)
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


if __name__ == "__main__":
    main() 