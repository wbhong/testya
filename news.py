import json
import requests
from bs4 import BeautifulSoup
import schedule
import time
from datetime import datetime

# --- 설정 ---
SEARCH_QUERY = "파이썬 웹 스크래핑"  # 검색할 키워드
NAVER_NEWS_URL = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={SEARCH_QUERY}&sort=1"
# sort=1은 최신순 정렬을 의미합니다.
# -----------------

def scrape_news():
    """
    네이버 뉴스 검색 결과를 스크래핑하여 정보를 추출합니다.
    """
    print("=" * 50)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 뉴스 스크래핑 시작...")
    
    try:
        # 봇으로 인식되지 않도록 User-Agent 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(NAVER_NEWS_URL, headers=headers)
        response.raise_for_status() # HTTP 오류 발생 시 예외 발생
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 뉴스 항목을 포함하는 컨테이너 찾기 (네이버 뉴스 현재 구조 기준)
        news_items = soup.select('div.news_area')
        
        if not news_items:
            print("❗ 스크래핑할 뉴스 항목을 찾을 수 없습니다. (선택자 확인 필요)")
            print("-" * 50)
            return

        summarized_data = []

        for item in news_items:
            # 1. 제목 및 링크 추출
            title_link = item.select_one('a.news_tit')
            title = title_link.get('title') if title_link else "제목 없음"
            url = title_link.get('href') if title_link else "#"

            # 2. 언론사 추출
            source_tag = item.select_one('a.info.press')
            source = source_tag.text.strip() if source_tag else "언론사 정보 없음"
            
            # 3. 업로드 일자 추출 (업로드 일자 태그가 정확하지 않을 수 있어, 뉴스 그룹 전체에서 찾음)
            date_tag = item.select_one('.info_group .info:not(.press)')
            upload_date = date_tag.text.strip() if date_tag and "시간" not in date_tag.text and "분" not in date_tag.text else "날짜 정보 없음"
            # 네이버는 'n시간 전' 같은 상대 시간을 많이 사용하므로, 정확한 날짜가 아니면 '날짜 정보 없음' 처리

            summarized_data.append({
                'title': title,
                'source': source,
                'date': upload_date,
                'url': url
            })

        print(f"✔️ 총 {len(summarized_data)}개의 뉴스 정보를 추출했습니다.\n")
        
        # 요약 정보 출력
        print("--- 뉴스 요약 정보 ---")
        for idx, news in enumerate(summarized_data, 1):
            print(f"[{idx}]")
            print(f"  📌 제목: {news['title']}")
            print(f"  🏢 언론사: {news['source']}")
            print(f"  📅 업로드 일자: {news['date']}")
            print(f"  🔗 링크: {news['url']} (이 주소를 복사하여 브라우저에서 클릭하여 이동)")
            print("-" * 20)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 요청 오류 발생: {e}")
    except Exception as e:
        print(f"❌ 스크래핑 중 예상치 못한 오류 발생: {e}")
        
    print("=" * 50)


def main():
    """
    뉴스 스크래핑 작업을 예약하고 주기적으로 실행합니다.
    """
    print(f"🔔 키워드: '{SEARCH_QUERY}' 뉴스 스크래핑을 시작합니다.")
    print("   매 1시간마다 작업을 실행하도록 설정되었습니다.")
    
    # 처음 한 번 즉시 실행
    scrape_news()
    
    # 매 1시간마다 scrape_news 함수 실행 예약
    schedule.every(1).hour.do(scrape_news)
    # 다른 예시: schedule.every(5).minutes.do(scrape_news) # 5분마다
    # 다른 예시: schedule.every().day.at("10:30").do(scrape_news) # 매일 10시 30분에
    
    while True:
        schedule.run_pending()
        time.sleep(1) # CPU 부하를 줄이기 위해 1초 대기

if __name__ == "__main__":
    main()
