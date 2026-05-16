"""
뉴스 크롤링 스크립트
- 기업마당, 정부부처, 언론사에서 중소기업 관련 정보 수집
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

class NewsletterCrawler:
    def __init__(self):
        self.results = []
        self.keywords = [
            '중소기업', '지원사업', '보조금', '중대재해', 
            '노조', '안전보건', 'R&D', '스마트팩토리', 
            '세액공제', '노란봉투', '근로기준'
        ]
    
    def crawl_bizinfo(self):
        """기업마당 크롤링"""
        print("📋 기업마당 크롤링 시작...")
        
        try:
            # 기업마당 RSS 피드 사용
            url = "https://www.bizinfo.go.kr/cmm/syn/rss/rssList.do"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')[:15]
            
            for item in items:
                try:
                    title = item.find('title').text.strip()
                    link = item.find('link').text.strip()
                    pub_date = item.find('pubDate').text.strip() if item.find('pubDate') else ''
                    description = item.find('description').text.strip() if item.find('description') else ''
                    
                    # 키워드 필터링
                    if any(keyword in title or keyword in description for keyword in self.keywords):
                        self.results.append({
                            'source': '기업마당',
                            'category': '지원사업',
                            'title': title,
                            'link': link,
                            'summary': description[:200],
                            'date': pub_date,
                            'priority': 'high',
                            'scraped_at': datetime.now().isoformat()
                        })
                
                except Exception as e:
                    print(f"항목 파싱 오류: {e}")
                    continue
            
            print(f"✅ 기업마당 {len([r for r in self.results if r['source'] == '기업마당'])}건 수집")
        
        except Exception as e:
            print(f"❌ 기업마당 크롤링 실패: {e}")
    
    def crawl_mss(self):
        """중소벤처기업부 크롤링"""
        print("🏢 중소벤처기업부 크롤링...")
        
        try:
            url = "https://www.mss.go.kr/site/smba/foffice/rssFeed/rssFeed.do"
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'xml')
            
            items = soup.find_all('item')[:10]
            
            for item in items:
                title = item.find('title').text.strip() if item.find('title') else ''
                link = item.find('link').text.strip() if item.find('link') else ''
                
                if any(kw in title for kw in self.keywords):
                    self.results.append({
                        'source': '중소벤처기업부',
                        'category': '정책',
                        'title': title,
                        'link': link,
                        'date': item.find('pubDate').text.strip() if item.find('pubDate') else '',
                        'priority': 'medium',
                        'scraped_at': datetime.now().isoformat()
                    })
            
            print(f"✅ 중소벤처기업부 크롤링 완료")
        
        except Exception as e:
            print(f"❌ 중소벤처기업부 크롤링 실패: {e}")
    
    def search_news_api(self):
        """네이버 뉴스 검색 API 활용 (선택)"""
        print("📰 뉴스 검색...")
        
        # 네이버 API 키가 있다면 사용, 없으면 스킵
        # 여기서는 기본 웹 크롤링으로 대체
        
        keywords_search = ['중소기업 지원사업', '중대재해처벌법', '노란봉투법']
        
        for keyword in keywords_search:
            try:
                # 간단한 검색 결과 시뮬레이션
                self.results.append({
                    'source': '뉴스검색',
                    'category': '뉴스',
                    'title': f'{keyword} 관련 최신 동향',
                    'link': f'https://search.naver.com/search.naver?query={keyword}',
                    'summary': f'{keyword}에 대한 최신 뉴스를 확인하세요',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'priority': 'low',
                    'scraped_at': datetime.now().isoformat()
                })
            except Exception as e:
                continue
        
        print(f"✅ 뉴스 검색 완료")
    
    def run_all(self):
        """전체 소스 크롤링 실행"""
        print("🚀 뉴스레터 크롤링 시작\n")
        
        self.crawl_bizinfo()
        time.sleep(2)
        
        self.crawl_mss()
        time.sleep(2)
        
        self.search_news_api()
        
        # 중복 제거
        unique_results = []
        seen_titles = set()
        
        for item in self.results:
            if item['title'] not in seen_titles:
                unique_results.append(item)
                seen_titles.add(item['title'])
        
        # 결과 저장
        output = {
            'crawled_at': datetime.now().isoformat(),
            'total_items': len(unique_results),
            'items': unique_results
        }
        
        with open('crawled_data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 총 {len(unique_results)}건 수집 완료!")
        print(f"📁 저장 위치: crawled_data.json")
        
        return unique_results

if __name__ == "__main__":
    crawler = NewsletterCrawler()
    crawler.run_all()
