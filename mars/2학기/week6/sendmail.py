# sendmail.py
# -*- coding: utf-8 -*-

import json
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Tuple


def load_credentials(file_path: str = 'credentials.json') -> Tuple[str, str]:
    """credentials.json 파일에서 sender와 password를 읽어 반환한다."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'credentials 파일을 찾을 수 없습니다: {file_path}')

    try:
        with open(file_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ValueError('credentials.json 파일의 JSON 형식이 잘못되었습니다.') from exc

    sender = data.get('sender')
    password = data.get('password')

    if not sender or not password:
        raise ValueError('credentials.json에 "sender"와 "password" 키가 모두 있어야 합니다.')

    return sender, password


def create_message(sender: str, receiver: str, subject: str, body: str) -> MIMEMultipart:
    """텍스트 본문을 가진 MIMEMultipart 메시지를 생성한다."""
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    return msg


def add_attachment(msg: MIMEMultipart, file_path: str) -> None:
    """첨부파일을 MIME 파트로 만들어 메시지에 추가한다."""
    if not file_path:
        return

    if not os.path.exists(file_path):
        raise FileNotFoundError(f'첨부파일을 찾을 수 없습니다: {file_path}')

    with open(file_path, 'rb') as fh:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(fh.read())

    encoders.encode_base64(part)
    filename = os.path.basename(file_path)
    part.add_header('Content-Disposition', f'attachment; filename={filename}')
    msg.attach(part)


def send_email(sender: str, password: str, receiver: str, subject: str,
               body: str, attachment_path: Optional[str] = None) -> None:
    """Gmail SMTP로 메일을 전송한다 (TLS 587)."""
    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    server = None

    msg = create_message(sender, receiver, subject, body)

    if attachment_path:
        try:
            add_attachment(msg, attachment_path)
        except FileNotFoundError as exc:
            print(f'첨부파일 오류: {exc}')
            print('첨부파일 없이 메일을 보냅니다.')

    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=20)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.send_message(msg)
        print('메일 전송 성공!')
    except smtplib.SMTPAuthenticationError:
        print('인증 실패: 이메일 또는 앱 비밀번호를 확인하세요.')
    except smtplib.SMTPConnectError:
        print('SMTP 서버에 연결할 수 없습니다.')
    except Exception as exc:
        print(f'메일 전송 중 오류 발생: {exc}')
    finally:
        if server:
            try:
                server.quit()
            except Exception:
                pass


def main() -> None:
    """프로그램 진입점: credentials.json을 읽고 사용자 입력으로 메일 전송."""
    try:
        sender, password = load_credentials()
    except (FileNotFoundError, ValueError) as exc:
        print(f'자격 증명 로드 실패: {exc}')
        print('해결 방법:')
        print('  1) 프로젝트 폴더에 credentials.json 파일이 있는지 확인하세요.')
        print('  2) 파일 형식은 {"sender":"you@gmail.com","password":"app_password"} 이어야 합니다.')
        return

    receiver = input('받는 사람 이메일을 입력하세요: ').strip()
    if not receiver:
        print('받는 사람 이메일을 입력해야 합니다.')
        return

    subject = input('메일 제목을 입력하세요 (기본: 테스트 메일): ').strip() or '테스트 메일'
    body = input('메일 본문을 입력하세요 (기본 문구 사용 시 Enter): ').strip() or '안녕하세요. 테스트 메일입니다.'
    attach_choice = input('첨부파일을 추가하시겠습니까? (y/n): ').strip().lower()
    attachment = None
    if attach_choice == 'y':
        attachment = input('첨부파일 경로를 입력하세요: ').strip()
        if not attachment:
            attachment = None

    send_email(sender, password, receiver, subject, body, attachment)


if __name__ == '__main__':
    main()
