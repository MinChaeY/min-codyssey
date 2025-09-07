import io
import string
import time
import multiprocessing
import pyzipper

# ✅ 테스트 ZIP 파일 생성 함수 (비밀번호 설정 가능)
def create_test_zip(password: str) -> bytes:
    buffer = io.BytesIO()
    with pyzipper.AESZipFile(buffer, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
        zf.setpassword(password.encode())
        zf.writestr('password.txt', 'This is a secret message.')
    return buffer.getvalue()

# ✅ 문자 조합 설정
CHARSET = string.ascii_lowercase + string.digits

# ✅ 공유 변수 정의
FOUND = multiprocessing.Value('b', False)
COUNTER = multiprocessing.Value('i', 0)

# ✅ 해킹 시도 함수 (메모리 기반 ZIP, 병렬 탐색)
def try_passwords(start_prefix, zip_bytes):
    print(f'[{start_prefix}] 프로세스 시작')
    try:
        with io.BytesIO(zip_bytes) as mem_zip:
            with pyzipper.AESZipFile(mem_zip, 'r') as zf:
                for c1 in CHARSET:
                    for c2 in CHARSET:
                        for c3 in CHARSET:
                            for c4 in CHARSET:
                                for c5 in CHARSET:
                                    if FOUND.value:
                                        return
                                    password = start_prefix + c1 + c2 + c3 + c4 + c5
                                    with COUNTER.get_lock():
                                        COUNTER.value += 1
                                    try:
                                        zf.setpassword(password.encode())
                                        content = zf.read('password.txt').decode('utf-8')
                                        with FOUND.get_lock():
                                            FOUND.value = True
                                        print(f'[✓] 비밀번호 찾음: {password}')
                                        print(f'[✓] 압축 해제 내용: {content}')
                                        return
                                    except:
                                        continue
    except Exception as e:
        print(f'[!] 오류: {e}')

# ✅ 전체 해킹 함수
def unlock_zip_memory(zip_bytes):
    start = time.time()
    print('🔓 메모리 기반 ZIP 해킹 시작')

    processes = []
    for ch in CHARSET:
        p = multiprocessing.Process(target=try_passwords, args=(ch, zip_bytes))
        p.start()
        processes.append(p)

    try:
        for p in processes:
            p.join()
    except KeyboardInterrupt:
        print('\n[!] 사용자 중단 → 프로세스 강제 종료')
        for p in processes:
            if p.is_alive():
                p.terminate()

    elapsed = time.time() - start
    print(f'\n총 시도 횟수: {COUNTER.value:,}')
    print(f'총 소요 시간: {elapsed:.2f}초')

# ✅ 실행
if __name__ == '__main__':
    zip_data = create_test_zip(password='abc123')  # 여기서 테스트용 암호 설정
    unlock_zip_memory(zip_data)
