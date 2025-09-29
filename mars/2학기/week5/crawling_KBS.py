import requests
from bs4 import BeautifulSoup


def fetch_kbs_headlines():
    """
    KBS 뉴스 웹사이트에서 주요 헤드라인 뉴스 제목을 추출한다.
    BeautifulSoup을 사용하여 HTML 파싱을 수행한다.
    """
    url = 'https://news.kbs.co.kr/news/pc/main/main.html'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers, timeout=5)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    # 개발자 도구(F12)에서 '헤드라인 뉴스'의 고유 selector(class/id)를 확인해야 함
    headline_tags = soup.select('p.title')  # 예시

    news_list = []
    for tag in headline_tags:
        title = tag.get_text(strip=True)
        if title:
            news_list.append(title)
            

    return news_list


def main():
    news_list = fetch_kbs_headlines()
    # 맨 앞(추천 인기 키워드)과 맨 뒤(공유하기) 제거
    if len(news_list) > 2:  # 최소 2개 이상 있을 때만 잘라내기
        news_list = news_list[1:-1]


    print('KBS 주요 뉴스 헤드라인:')
    for idx, news in enumerate(news_list, start=1):
        print(f'{idx}. {news}')


if __name__ == '__main__':
    main()
