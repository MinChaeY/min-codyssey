# door_hacking.py
import zipfile
import string
import time
import multiprocessing
import os  # 강제 종료용

# 문자 조합 설정
CHARSET = string.ascii_lowercase + string.digits

# 경로 설정 (원하는 경로로 수정)
ZIP_PATH = 'E:\\min-codyssey\\mars\\week9\\emergency_storage_key.zip'
TARGET_FILE = 'password.txt'
PASSWORD_OUTPUT = 'E:\\min-codyssey\\mars\\week9\\password.txt'
CONTENT_OUTPUT = 'E:\\min-codyssey\\mars\\week9\\decrypted_password_content.txt'

# 공유 변수
FOUND = multiprocessing.Value('b', False)
COUNTER = multiprocessing.Value('i', 0)

def try_passwords(start_prefix):
    print(f'[{start_prefix}] 프로세스 시작')
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zf:
            for c1 in CHARSET:
                for c2 in CHARSET:
                    for c3 in CHARSET:
                        for c4 in CHARSET:
                            for c5 in CHARSET:
                                password = start_prefix + c1 + c2 + c3 + c4 + c5
                                with COUNTER.get_lock():
                                    COUNTER.value += 1
                                if FOUND.value:
                                    return
                                try:
                                    with zf.open(TARGET_FILE, pwd=password.encode()) as f:
                                        content = f.read().decode('utf-8', errors='replace')

                                        # 비밀번호 저장 (문제 조건 충족)
                                        with open(PASSWORD_OUTPUT, 'w') as pwfile:
                                            pwfile.write(password + '\n')
                                        #  압축 해제된 파일 내용 저장
                                        with open(CONTENT_OUTPUT, 'w') as outfile:
                                            outfile.write(content)

                                        with FOUND.get_lock():
                                            FOUND.value = True

                                        print(f'[✓] 비밀번호 찾음: {password}')
                                        # 프로그램 전체 강제 종료
                                        os._exit(0)  # 즉시 전체 종료
                                except:
                                    continue
    except Exception as e:
        print(f'[!] 오류 발생: {e}')

def unlock_zip():
    start = time.time()
    print('시작 시간:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))

    processes = []
    for ch in CHARSET:
        p = multiprocessing.Process(target=try_passwords, args=(ch,))
        p.start()
        processes.append(p)

    try:
        while True:
            if FOUND.value:
                print(' 비밀번호 찾음 → 프로세스 종료 중...')
                for p in processes:
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=2)  # 안정적 종료 대기
                break

            if all(not p.is_alive() for p in processes):
                break

            time.sleep(0.2)

    except KeyboardInterrupt:
        print('\n 사용자 중단 → 모든 프로세스 강제 종료')
        for p in processes:
            if p.is_alive():
                p.terminate()

    elapsed = time.time() - start
    print(f'총 시도 횟수: {COUNTER.value:,}')
    print(f'총 소요 시간: {elapsed:.2f}초')

if __name__ == '__main__':
    unlock_zip()
