# sendmail.py
# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# Gmail SMTP 메일 전송 프로그램
# - credentials.json 파일에서 이메일/비밀번호를 읽어옴
# - 제목, 본문, 첨부파일을 포함한 메일을 전송
# - 예외 처리 및 사용자 입력 기능 포함
# ------------------------------------------------------------

# ---------- 라이브러리 임포트 ----------
# json : credentials.json 파일 읽기
# os : 파일 경로 확인
# smtplib : SMTP 프로토콜을 이용해 메일 서버 연결
# email 모듈 : 메일의 본문, 첨부파일 등을 구성 ->컨테이너 생성 모듈
# typing : 타입 힌트 제공
import json
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Tuple


# ------------------------------------------------------------
# credentials.json 파일을 읽어 이메일 정보 불러오기
# ------------------------------------------------------------
def load_credentials(file_path: str = 'credentials.json') -> Tuple[str, str]:
    """credentials.json 파일에서 sender와 password를 읽어 반환한다."""

    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'credentials 파일을 찾을 수 없습니다: {file_path}')

    try:
        # 파일을 열고 JSON 데이터로 읽기
        with open(file_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        # JSON 문법이 잘못된 경우 오류 발생
        raise ValueError('credentials.json 파일의 JSON 형식이 잘못되었습니다.') from exc

    # JSON에서 sender(이메일), password(앱 비밀번호) 키 가져오기
    sender = data.get('sender')
    password = data.get('password')

    # 두 값이 모두 존재하는지 검증
    if not sender or not password:
        raise ValueError('credentials.json에 "sender"와 "password" 키가 모두 있어야 합니다.')

    # 이메일과 비밀번호 반환
    return sender, password


# ------------------------------------------------------------
# 메일 본문(텍스트)을 포함한 메시지 객체 생성
# ------------------------------------------------------------
def create_message(sender: str, receiver: str, subject: str, body: str) -> MIMEMultipart:
    """텍스트 본문을 가진 MIMEMultipart 메시지를 생성한다."""

    # MIMEMultipart : 여러 파트(본문, 첨부파일 등)를 담는 컨테이너
    msg = MIMEMultipart()

    # 메일 기본 정보 설정
    msg['From'] = sender        # 보내는 사람 주소
    msg['To'] = receiver        # 받는 사람 주소
    msg['Subject'] = subject    # 메일 제목

    # 본문 텍스트 추가 (plain은 일반 텍스트 형식)
    msg.attach(MIMEText(body, 'plain'))

    # 구성된 메일 객체 반환
    return msg


# ------------------------------------------------------------
# 첨부파일을 MIME 형식으로 메일 객체에 추가
# ------------------------------------------------------------
def add_attachment(msg: MIMEMultipart, file_path: str) -> None:
    """첨부파일을 MIME 파트로 만들어 메시지에 추가한다."""

    # 첨부파일 경로가 비어 있으면 함수 종료
    if not file_path:
        print('첨부파일 경로가 유효하지 않습니다. 첨부파일 없이 전송합니다.')
        return

    # 파일 존재 여부 확인
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'첨부파일을 찾을 수 없습니다: {file_path}')

    # 파일을 바이너리 모드로 읽어서 payload(본문 데이터)에 담기
    with open(file_path, 'rb') as fh:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(fh.read())

    # SMTP 전송을 위해 Base64로 인코딩 -> 이메일은 원래 바이너리 데이터를 직접 전송하지 않음. 텍스트 기반 프로토콜이므로 인코딩 필요해서 사용
    encoders.encode_base64(part)

    # 파일 이름을 Content-Disposition 헤더에 추가
    filename = os.path.basename(file_path)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')

    # 메일 객체(msg)에 첨부파일 파트 추가
    msg.attach(part)


# ------------------------------------------------------------
# SMTP 서버에 연결해 메일을 실제로 전송하는 함수 SMTP = 메일 전송 규약
# ------------------------------------------------------------
def send_email(sender: str, password: str, receiver: str, subject: str,
               body: str, attachment_path: Optional[str] = None) -> None:
    """Gmail SMTP로 메일을 전송한다 (TLS 587)."""

    # Gmail SMTP 서버 설정
    smtp_host = 'smtp.gmail.com'   # Gmail SMTP 주소 / 보내는 메일의 주소 형식은 상관 없음. gmail.com만 맞으면 됨.
    smtp_port = 587                # TLS 연결용 포트 -> smtp 암호화 통신 tls 암호화 통신이 587을 사용함. = tls 암호화로 smtp 통신을 시행
    server = None                  # 서버 객체 초기화 (나중에 할당) None이 아닐 경우 finally에서 종료 시도

    # 메일 메시지 생성 (본문 포함)
    msg = create_message(sender, receiver, subject, body)

    # 첨부파일이 있는 경우 추가 시도
    if attachment_path:
        try:
            add_attachment(msg, attachment_path)
        except FileNotFoundError as exc:
            # 파일을 찾지 못한 경우 경고 출력 후 첨부 없이 전송
            print(f'첨부파일 오류: {exc}')
            print('첨부파일 없이 메일을 보냅니다.')

    # SMTP 연결 및 전송 시도
    try:
        # SMTP 서버에 연결
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)

        # 서버와의 연결 확인
        server.ehlo()

        # TLS(암호화) 연결 시작 -> 암호화 통신 시작
        server.starttls()

        # 암호화된 상태에서 다시 EHLO (SMTP 관례) -> Extended Hello 서버와 클라이언트가 서로의 기능을 확인하는 절차
        server.ehlo()

        # Gmail 로그인 (앱 비밀번호 사용)
        server.login(sender, password)

        # 메일 전송
        server.send_message(msg)
        print('메일 전송 성공!')

    # 로그인 실패 예외
    except smtplib.SMTPAuthenticationError:
        print('인증 실패: 이메일 또는 앱 비밀번호를 확인하세요.')

    # 서버 연결 실패 예외
    except smtplib.SMTPConnectError:
        print('SMTP 서버에 연결할 수 없습니다.')

    # 그 외 모든 예외 처리
    except Exception as exc:
        print(f'메일 전송 중 오류 발생: {exc}')

    # 연결 종료 (finally 블록은 항상 실행)
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                # 서버 종료 중 오류 발생해도 무시
                pass


# ------------------------------------------------------------
# 프로그램의 시작점 (사용자 입력 → 메일 전송)
# ------------------------------------------------------------
def main() -> None:
    """프로그램 진입점: credentials.json을 읽고 사용자 입력으로 메일 전송."""

    # 1) credentials.json에서 계정 정보 불러오기
    try:
        sender, password = load_credentials()
    except (FileNotFoundError, ValueError) as exc:
        # 파일이 없거나 형식이 잘못된 경우 안내 메시지 출력 후 종료
        print(f'자격 증명 로드 실패: {exc}')
        print('해결 방법:')
        print('  1) 프로젝트 폴더에 credentials.json 파일이 있는지 확인하세요.')
        print('  2) 파일 형식은 {"sender":"you@gmail.com","password":"app_password"} 이어야 합니다.')
        return

    # 2) 사용자로부터 메일 관련 입력 받기
    receiver = input('받는 사람 이메일을 입력하세요: ').strip()
    if not receiver:
        print('받는 사람 이메일을 입력해야 합니다.')
        return

    # 메일 제목과 본문 입력 (기본값 제공)
    subject = input('메일 제목을 입력하세요 (기본: 테스트 메일): ').strip() or '테스트 메일'
    body = input('메일 본문을 입력하세요 (기본 문구 사용 시 Enter): ').strip() or '안녕하세요. 테스트 메일입니다.'

    # 첨부파일 여부 확인
    attach_choice = input('첨부파일을 추가하시겠습니까? (y/n): ').strip().lower()
    attachment = None
    if attach_choice == 'y':
        attachment = input('첨부파일 경로를 입력하세요: ').strip()
        if not attachment:
            attachment = None
            print('첨부파일 경로가 유효하지 않습니다. 첨부파일 없이 전송합니다.')

    # 3) 메일 전송 함수 호출
    send_email(sender, password, receiver, subject, body, attachment)


# ------------------------------------------------------------
# Python 프로그램의 시작 지점
# ------------------------------------------------------------
if __name__ == '__main__':
    # main() 함수 실행
    main()
