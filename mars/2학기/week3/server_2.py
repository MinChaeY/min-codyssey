import socket
import threading
from datetime import datetime
import os

HOST = ""          # 모든 인터페이스 바인드
PORT = 8080        # 포트 번호
BACKLOG = 50       # 대기열 크기
READ_SIZE = 8192   # 초기 요청 읽기 버퍼
INDEX_PATH = "index.html"

# 종료 신호 (메인 스레드에서 'q' 입력 시 set)
stop_event = threading.Event()

def http_response(status_line: str, headers: dict | None, body: bytes | None) -> bytes:
    """HTTP/1.1 응답 패킷 조립"""
    lines = [status_line]
    headers = headers or {}

    # Content-Length 자동 보정
    if body is not None and "Content-Length" not in headers:
        headers["Content-Length"] = str(len(body))

    # 기본 연결 정책: close
    headers.setdefault("Connection", "close")
    # 서버 식별자(선택)
    headers.setdefault("Server", "PirateSocket/1.0")

    # 헤더 직렬화
    for k, v in headers.items():
        lines.append(f"{k}: {v}")
    lines.append("")  # 빈 줄
    head = "\r\n".join(lines).encode("utf-8")

    return head + (body or b"")

def serve_204_no_content() -> bytes:
    return http_response("HTTP/1.1 204 No Content", {}, None)

def serve_404() -> bytes:
    body = b"File Not Found"
    headers = {
        "Content-Type": "text/plain; charset=utf-8",
    }
    return http_response("HTTP/1.1 404 Not Found", headers, body)

def serve_500(msg: str = "Internal Server Error") -> bytes:
    body = msg.encode("utf-8", errors="ignore")
    headers = {"Content-Type": "text/plain; charset=utf-8"}
    return http_response("HTTP/1.1 500 Internal Server Error", headers, body)

def serve_index() -> bytes:
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        body = html.encode("utf-8")
        headers = {
            "Content-Type": "text/html; charset=utf-8",
        }
        return http_response("HTTP/1.1 200 OK", headers, body)
    except FileNotFoundError:
        return serve_404()

def parse_request_line(request_bytes: bytes) -> tuple[str, str, str]:
    """
    요청 첫 줄 파싱: b"GET /path HTTP/1.1\r\n..."
    반환: (method, path, version)
    """
    try:
        text = request_bytes.decode("iso-8859-1", errors="ignore")
        first_line = text.split("\r\n", 1)[0]
        method, path, version = first_line.split(" ")
        return method, path, version
    except Exception:
        # 형식이 이상한 경우 기본값
        return "", "", ""

def handle_client(conn: socket.socket, addr: tuple[str, int]):
    """
    단일 클라이언트 연결 처리
    - 요청 라인만 가볍게 파싱
    - favicon, /, /index.html 분기
    """
    try:
        # 헤더까지만 읽으면 충분 (간단 서버)
        request = conn.recv(READ_SIZE)
        if not request:
            return

        method, path, version = parse_request_line(request)
        # 간단 서버라 GET만 허용
        if method != "GET":
            resp = http_response(
                "HTTP/1.1 405 Method Not Allowed",
                {"Content-Type": "text/plain; charset=utf-8", "Allow": "GET"},
                b"Method Not Allowed",
            )
            conn.sendall(resp)
            return

        # favicon 무시
        if path == "/favicon.ico":
            conn.sendall(serve_204_no_content())
            return

        # 라우팅
        if path in ("/", "/index.html"):
            resp = serve_index()

            # 로그 (성공시에만)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{now}] 클라이언트 접속 IP: {addr[0]}")
        else:
            resp = serve_404()

        conn.sendall(resp)

    except Exception as e:
        try:
            conn.sendall(serve_500(str(e)))
        except Exception:
            pass
    finally:
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass
        conn.close()

def accept_loop(server_sock: socket.socket):
    """
    수락(accept) 루프
    - settimeout으로 주기적으로 stop_event 확인
    """
    # 진행 중 클라이언트 스레드 추적(선택)
    client_threads: list[threading.Thread] = []

    server_sock.settimeout(1.0)  # 1초마다 깨어나 종료 여부 확인
    print(f"HTTP 서버가 {PORT}번 포트에서 시작되었습니다...")

    try:
        while not stop_event.is_set():
            try:
                conn, addr = server_sock.accept()
            except socket.timeout:
                continue  # 종료 신호 확인 재시도
            except OSError:
                # 소켓이 닫히면 accept에서 OSError가 날 수 있음
                break

            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()
            client_threads.append(t)

    finally:
        # 새로운 연결은 더 이상 받지 않도록 소켓 닫기
        try:
            server_sock.close()
        except Exception:
            pass

        # 기존 처리 중이던 요청은 마무리될 수 있게 잠깐 대기
        # (daemon=True라 프로세스 종료 시 강제 종료되지만, 약간의 정리 시간을 준다)
        for t in client_threads:
            t.join(timeout=2.0)

        print("HTTP 서버가 정상 종료되었습니다.")

def run_server():
    # 서버 소켓 준비
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 재시작 시 TIME_WAIT 포트 충돌 줄이기
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(BACKLOG)

    # 서버 수락 루프 스레드
    t_accept = threading.Thread(target=accept_loop, args=(server_sock,), daemon=True)
    t_accept.start()

    # 관리자 입력 루프
    try:
        while True:
            cmd = input("명령어 입력 (q 입력 시 서버 종료): ").strip().lower()
            if cmd == "q":
                print("서버 종료 중...")
                stop_event.set()
                break
    except KeyboardInterrupt:
        print("\n[Ctrl+C] 서버 종료 중...")
        stop_event.set()
    finally:
        # accept 루프가 settimeout 주기로 종료되며, 소켓도 닫힘
        t_accept.join()

if __name__ == "__main__":
    run_server()
