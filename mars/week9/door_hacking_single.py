# door_hacking_single.py
import zipfile
import string
import time

# 문자 조합 설정
CHARSET = string.ascii_lowercase + string.digits

# 경로 설정 (필요 시 수정)
ZIP_PATH = 'E:\min-codyssey\mars\week9\emergency_storage_key.zip'
TARGET_FILE = 'password.txt'
PASSWORD_OUTPUT = 'E:\min-codyssey\mars\week9\password.txt'
CONTENT_OUTPUT = 'E:\min-codyssey\mars\week9\decrypted_password_content.txt'

def unlock_zip():
    start = time.time()
    print(' 시작 시간:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))

    attempt = 0

    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            for c1 in CHARSET:
                for c2 in CHARSET:
                    for c3 in CHARSET:
                        for c4 in CHARSET:
                            for c5 in CHARSET:
                                for c6 in CHARSET:
                                    password = c1 + c2 + c3 + c4 + c5 + c6
                                    attempt += 1
                                    try:
                                        with zf.open(TARGET_FILE, pwd=password.encode()) as f:
                                            content = f.read().decode('utf-8', errors='replace')

                                            with open(PASSWORD_OUTPUT, 'w') as pwfile:
                                                pwfile.write(password + '\n')

                                            with open(CONTENT_OUTPUT, 'w') as outfile:
                                                outfile.write(content)

                                            print(f'[✓] 비밀번호 찾음: {password}')
                                            elapsed = time.time() - start
                                            print(f' 총 시도 횟수: {attempt:,}')
                                            print(f' 총 소요 시간: {elapsed:.2f}초')
                                            return
                                    except:
                                        if attempt % 10000000 == 0:
                                            print(f'...{attempt:,}회 시도 중...')

        print('실패: 가능한 모든 조합을 시도했지만 비밀번호를 찾지 못했습니다.')

    except FileNotFoundError:
        print(f'[!] zip 파일을 찾을 수 없습니다: {ZIP_PATH}')

if __name__ == '__main__':
    unlock_zip()
