# door_hacking.py
import zipfile
import string
import time
import multiprocessing

# 암호 조합 문자 (소문자 + 숫자)
CHARSET = string.ascii_lowercase + string.digits

# 경로 설정 (필요 시 수정)
ZIP_PATH = 'E:\min-codyssey\mars\week9\emergency_storage_key.zip'
TARGET_FILE = 'password.txt'  # zip 안 파일명
PASSWORD_OUTPUT = 'E:\min-codyssey\mars\week9\password.txt'  # 암호 저장 (문제 조건 충족)
CONTENT_OUTPUT = 'E:\min-codyssey\mars\week9\decrypted_password_content.txt'  # 압축 내용 저장

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
                                        # 비밀번호 저장 (조건 충족)
                                        with open(PASSWORD_OUTPUT, 'w') as pwfile:
                                            pwfile.write(password + '\n')
                                        # 압축 해제된 파일 내용 별도 저장
                                        with open(CONTENT_OUTPUT, 'w') as outfile:
                                            outfile.write(content)
                                        with FOUND.get_lock():
                                            FOUND.value = True
                                        print(f'[✓] 비밀번호 찾음: {password}')
                                        return
                                except:
                                    continue
    except Exception as e:
        print(f'[!] 오류 발생: {e}')

def unlock_zip():
    start = time.time()
    print(' 시작 시간:', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))

    processes = []
    for ch in CHARSET:
        p = multiprocessing.Process(target=try_passwords, args=(ch,))
        p.start()
        processes.append(p)

    # 암호 찾으면 즉시 종료 + 완전한 정리
    while True:
        if FOUND.value:
            print('비밀번호 찾음 → 모든 프로세스 종료 중...')
            for p in processes:
                if p.is_alive():
                    p.terminate()
                    p.join()  # 종료 대기
            break

        if all(not p.is_alive() for p in processes):
            break

        time.sleep(0.2)  # 너무 자주 확인하지 않도록 간격 둠

    elapsed = time.time() - start
    print(f'총 시도 횟수: {COUNTER.value:,}')
    print(f'총 소요 시간: {elapsed:.2f}초')

if __name__ == '__main__':
    unlock_zip()
