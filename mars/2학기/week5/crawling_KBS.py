from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time, random

class NaverCrawler:
    """네이버 로그인 및 콘텐츠 크롤링 클래스"""

    def __init__(self, user_id: str, user_pw: str) -> None:
        self.user_id = user_id
        self.user_pw = user_pw

        # 크롬 옵션 설정
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 흔적 제거
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")

        # User-Agent 변경 (사람 브라우저처럼 위장)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service()
        self.driver = webdriver.Chrome(service=service, options=options)

        # 자동화 탐지 속성 제거
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """},
        )

    def human_typing(self, element, text):
        """사람처럼 타이핑"""
        for ch in text:
            element.send_keys(ch)
            time.sleep(random.uniform(0.1, 0.3))

    def login(self) -> None:
        """네이버 로그인 수행"""
        self.driver.get('https://nid.naver.com/nidlogin.login')
        time.sleep(random.uniform(2, 4))

        # 아이디 입력
        id_box = self.driver.find_element(By.ID, 'id')
        self.human_typing(id_box, self.user_id)
        time.sleep(random.uniform(1, 2))

        # 비밀번호 입력
        pw_box = self.driver.find_element(By.ID, 'pw')
        self.human_typing(pw_box, self.user_pw)
        time.sleep(random.uniform(1, 2))

        # 로그인 버튼 클릭
        login_btn = self.driver.find_element(By.ID, 'log.login')
        login_btn.click()
        time.sleep(random.uniform(3, 5))

    def get_main_news_titles(self) -> list:
        """메인 뉴스 타이틀 크롤링 (로그인 후/전 비교 가능)"""
        self.driver.get('https://www.naver.com')
        time.sleep(random.uniform(3, 5))

        news_elements = self.driver.find_elements(By.CSS_SELECTOR, '.hdline_article_tit a')
        titles = [elem.text for elem in news_elements if elem.text.strip()]
        return titles

    def get_mail_titles(self) -> list:
        """네이버 메일 제목 크롤링"""
        self.driver.get('https://mail.naver.com')
        time.sleep(random.uniform(3, 6))

        mail_elements = self.driver.find_elements(By.CSS_SELECTOR, '.mail_title_link')
        mail_titles = [elem.text for elem in mail_elements if elem.text.strip()]
        return mail_titles

    def close(self) -> None:
        """드라이버 종료"""
        self.driver.quit()


def main():
    """메인 실행 함수"""
    # 아이디 비번 하드코딩
    user_id = "네이버ID"
    user_pw = "비밀번호"

    crawler = NaverCrawler(user_id, user_pw)

    print('=== 로그인 전 뉴스 타이틀 ===')
    before_titles = crawler.get_main_news_titles()
    print(before_titles)

    crawler.login()

    print('\n=== 로그인 후 뉴스 타이틀 ===')
    after_titles = crawler.get_main_news_titles()
    print(after_titles)

    print('\n=== 네이버 메일 제목 ===')
    mail_titles = crawler.get_mail_titles()
    print(mail_titles)

    crawler.close()


if __name__ == '__main__':
    main()
