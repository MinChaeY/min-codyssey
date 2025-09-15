import socket
import threading
import sys


class ChatClient:
    """콘솔 기반 채팅 클라이언트 (TCP/IP 라인 프로토콜 사용)."""

    def __init__(self, host: str = '127.0.0.1', port: int = 5000) -> None:
        # IPv4 + TCP 소켓 생성
        # (IP 계층에서 주소, TCP 계층에서 포트 지정)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.alive = False

    def start(self) -> None:
        """서버에 연결하고 송수신 스레드를 시작한다."""
        # TCP 3-Way Handshake (SYN → SYN/ACK → ACK) 후 세션 성립
        self.sock.connect((self.host, self.port))
        self.alive = True

        # 서버에서 오는 첫 메시지 수신 (사용자명 프롬프트)
        # recv()는 TCP 스트림에서 바이트 단위로 읽어옴 (세그먼트 경계와 무관)
        greeting = self.sock.recv(1024).decode('utf-8', errors='ignore')
        print(greeting, end='')

        # 사용자명 입력 후 '\n' 붙여 전송
        # sendall()은 내부적으로 send()를 반복 → 전체 바이트 송신 보장
        username = input().strip()
        if not username:
            username = 'User'
        self.sock.sendall((username + '\n').encode('utf-8'))

        # 별도 스레드에서 수신 루프 실행
        # TCP는 풀-듀플렉스라 송신과 수신을 동시에 수행 가능
        recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        recv_thread.start()

        # 메인 스레드: 사용자 입력 → 서버로 송신
        try:
            while self.alive:
                msg = input()
                if msg == '/종료':
                    # 애플리케이션 프로토콜 상 "종료 명령" 전송
                    self.sock.sendall(b'/\xec\xa2\x85\xeb\xa3\x8c\n')  # '/종료'
                    break
                # 일반 메시지 전송 (UTF-8 + 개행)
                self.sock.sendall((msg + '\n').encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            # Ctrl+D, Ctrl+C 등 입력 종료 처리
            pass
        finally:
            self.stop()

    def _recv_loop(self) -> None:
        """서버로부터 수신한 메시지를 출력한다."""
        try:
            while self.alive:
                # recv()는 커널의 TCP 수신 버퍼에서 읽어옴
                # 반환값이 빈 바이트열이면 상대가 FIN 전송 → 연결 종료
                data = self.sock.recv(4096)
                if not data:
                    break
                text = data.decode('utf-8', errors='ignore')
                print(text, end='')
        except (ConnectionResetError, OSError):
            # 서버 비정상 종료(RST) 등 예외
            pass
        finally:
            self.alive = False

    def stop(self) -> None:
        """소켓 정리 및 TCP 연결 종료."""
        self.alive = False
        try:
            # TCP 양방향 종료 (FIN 전송)
            self.sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        try:
            # 로컬 자원 해제, 소켓 FD 반환
            self.sock.close()
        except OSError:
            pass
        # 종료 후 클라이언트 측 TCP 소켓은 TIME_WAIT 상태에 잠시 머무름
        print('\n[INFO] 클라이언트를 종료했습니다.')


def main() -> None:
    """엔트리 포인트."""
    host = '127.0.0.1'
    port = 5000
    # 명령줄 인자에서 host, port 지정 가능
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
        # 서버가 LISTEN 중이 아니면 TCP 연결 시도 시 RST → 이 예외 발생
        print('[ERROR] 서버에 연결할 수 없습니다.')
        sys.exit(1)


if __name__ == '__main__':
    main()
