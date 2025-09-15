from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime


class PirateHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """클라이언트의 GET 요청 처리"""

         #원래 브라우저는 페이지를 열 때 index.html 뿐만 아니라 favicon.ico도 자동으로 요청.
         # 우리는 favicon.ico 파일을 제공 x 서버가 404 not found로 응답
         # 해당 로그 출력을 방지하기 위해 favicon 요청을 받으면 빈 응답을 주도록 요청 무시 처리
        if self.path == '/favicon.ico':
            self.send_response(204)  # 내용 없음
            self.end_headers()
            return

        # 루트("/") 또는 index.html 요청 처리 -> 그 이외에는 처리x
        if self.path == '/' or self.path == '/index.html':
            try:
                # index.html 파일 읽기
                with open('index.html', 'r', encoding='utf-8') as file: #파일을 읽기모드로 열기
                    content = file.read()

                # 응답 코드: 200 OK -> 요청을 성공적으로 처리함
                self.send_response(200)
                # 헤더 정보: HTML 문서 + UTF-8 인코딩
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # 파일 내용을 클라이언트(브라우저)에게 전송
                self.wfile.write(content.encode('utf-8'))

                # 접속 시간과 클라이언트 IP 서버 로그 출력
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                client_ip = self.client_address[0]
                print(f'[{now}] 클라이언트 접속 IP: {client_ip}')

            except FileNotFoundError:
                # index.html이 없을 경우 404 에러 반환
                self.send_error(404, 'File Not Found')
        else:
            # 지원하지 않는 경로일 경우 404 에러 반환
            self.send_error(404, 'File Not Found')


def run_server():
    """8080 포트에서 서버 실행"""
    port = 8080 
    server_address = ('', port)
    httpd = HTTPServer(server_address, PirateHandler)
    print(f'HTTP 서버가 {port}번 포트에서 시작되었습니다...')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
