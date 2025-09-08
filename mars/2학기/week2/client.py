import socket
import threading
import sys


class ChatClient:
    """콘솔 기반 채팅 클라이언트."""

    def __init__(self, host: str = '127.0.0.1', port: int = 5000) -> None:
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alive = False

    def start(self) -> None:
        """서버에 연결하고 송수신 스레드를 시작한다."""
        self.sock.connect((self.host, self.port))
        self.alive = True

        # 서버의 사용자명 프롬프트 수신 및 표시
        greeting = self.sock.recv(1024).decode('utf-8', errors='ignore')
        print(greeting, end='')

        # 사용자명 입력 후 전송
        username = input().strip()
        if not username:
            username = 'User'
        self.sock.sendall((username + '\n').encode('utf-8'))

        # 수신 스레드
        recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        recv_thread.start()

        # 송신 루프 (메인 스레드)
        try:
            while self.alive:
                msg = input()
                if msg == '/종료':
                    self.sock.sendall(b'/\xec\xa2\x85\xeb\xa3\x8c\n')  # '/종료'
                    break
                self.sock.sendall((msg + '\n').encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            pass
        finally:
            self.stop()

    def _recv_loop(self) -> None:
        """서버로부터 수신한 메시지를 출력한다."""
        try:
            while self.alive:
                data = self.sock.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8', errors='ignore')
                print(text, end='')
        except (ConnectionResetError, OSError):
            pass
        finally:
            self.alive = False

    def stop(self) -> None:
        """소켓 정리."""
        self.alive = False
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            self.sock.close()
        except OSError:
            pass
        print('\n[INFO] 클라이언트를 종료했습니다.')


def main() -> None:
    """엔트리 포인트."""
    host = '127.0.0.1'
    port = 5000
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print('[ERROR] 포트는 정수여야 합니다.')
            sys.exit(1)

    client = ChatClient(host=host, port=port)
    try:
        client.start()
    except ConnectionRefusedError:
        print('[ERROR] 서버에 연결할 수 없습니다.')
        sys.exit(1)


if __name__ == '__main__':
    main()