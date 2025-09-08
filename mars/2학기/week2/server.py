import socket
import threading
import signal
import sys
from typing import Dict, Tuple


class ChatServer:
    """멀티스레드 TCP 채팅 서버 구현 클래스."""

    def __init__(self, host: str = '0.0.0.0', port: int = 5000) -> None:
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 동일 포트 재시작 용이
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 클라이언트 관리: {conn: username}
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()
        self.running = False

    def start(self) -> None:
        """서버를 시작하고 연결 수락 루프에 진입한다."""
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(20)
        self.running = True
        print(f'[INFO] ChatServer listening on {self.host}:{self.port}')

        # 안전 종료 시그널 핸들링
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

        try:
            while self.running:
                try:
                    conn, addr = self.server_sock.accept()
                except OSError:
                    # 소켓이 이미 닫힌 경우
                    break

                thread = threading.Thread(
                    target=self._handle_client,
                    args=(conn, addr),
                    daemon=True
                )
                thread.start()
        finally:
            self._shutdown()

    def _handle_signal(self, signum, frame) -> None:
        """SIGINT/SIGTERM 시 안전 종료."""
        print('\n[INFO] Shutting down server...')
        self.running = False
        try:
            self.server_sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.server_sock.close()

    def _handle_client(self, conn: socket.socket, addr: Tuple[str, int]) -> None:
        """개별 클라이언트 연결을 처리한다."""
        conn.settimeout(300)  # 유휴 연결 방지 (선택)
        try:
            # 1) 최초로 사용자명 요청/수신
            conn.sendall('사용자명을 입력하세요: '.encode('utf-8'))
            username_bytes = conn.recv(1024)
            if not username_bytes:
                conn.close()
                return
            username = username_bytes.decode('utf-8').strip()

            # 사용자명 기본값 방어
            if not username:
                username = f'Guest-{addr[1]}'

            with self.lock:
                self.clients[conn] = username

            # 2) 입장 공지 브로드캐스트
            join_msg = f'{username}님이 입장하셨습니다.'
            self._broadcast(join_msg, exclude=None)

            # 3) 클라이언트로 사용 도움말 전송
            help_text = (
                "채팅에 참여합니다. '/종료'를 입력하면 연결이 종료됩니다.\n"
            )
            conn.sendall(help_text.encode('utf-8'))

            # 4) 메시지 루프
            while True:
                data = conn.recv(4096)
                if not data:
                    # 소켓이 닫힌 경우
                    break

                text = data.decode('utf-8', errors='ignore').rstrip('\r\n')

                if text == '/종료':
                    break

                # 빈 문자열은 무시
                if not text:
                    continue

                # '사용자> 메시지' 형식으로 전체 전송
                full = f'{username}> {text}'
                self._broadcast(full, exclude=None)

        except (ConnectionResetError, ConnectionAbortedError, TimeoutError):
            # 클라이언트 비정상 종료 등
            pass
        finally:
            self._remove_client(conn)

    def _broadcast(self, message: str, exclude: socket.socket | None) -> None:
        """모든 접속자에게 메시지를 전송한다."""
        to_remove = []
        with self.lock:
            for client, _name in self.clients.items():
                if exclude is not None and client == exclude:
                    continue
                try:
                    client.sendall((message + '\n').encode('utf-8'))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    to_remove.append(client)

            # 전송 실패한 클라이언트 정리
            for client in to_remove:
                self._remove_client(client)

        # 서버 콘솔에도 로깅
        print(f'[BROADCAST] {message}')

    def _remove_client(self, conn: socket.socket) -> None:
        """클라이언트를 목록에서 제거하고 퇴장 공지."""
        username = None
        with self.lock:
            if conn in self.clients:
                username = self.clients.pop(conn)

        try:
            conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            conn.close()
        except OSError:
            pass

        if username:
            leave_msg = f'{username}님이 퇴장하셨습니다.'
            self._broadcast(leave_msg, exclude=None)
            print(f'[INFO] Disconnected: {username}')

    def _shutdown(self) -> None:
        """서버 종료 시 모든 연결을 정리한다."""
        with self.lock:
            conns = list(self.clients.keys())

        for c in conns:
            self._remove_client(c)

        try:
            self.server_sock.close()
        except OSError:
            pass
        print('[INFO] Server closed.')


def main() -> None:
    """엔트리 포인트."""
    # 기본 포트: 5000. 필요 시 명령행 인자로 변경 가능.
    host = '0.0.0.0'
    port = 5000
    if len(sys.argv) >= 2:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print('[ERROR] 포트는 정수여야 합니다.')
            sys.exit(1)

    server = ChatServer(host=host, port=port)
    server.start()


if __name__ == '__main__':
    main()