# javis.py
import datetime # 날짜와 시간 관련 기능을 제공하는 파이썬 기본 모듈
from pathlib import Path # 파일 경로를 쉽게 디룰 수 있게 해줌
import sounddevice as sd # 마이크의 입력을 받아 녹음할 수 있게 해줌
from scipy.io.wavfile import write # 녹음한 데이터를 .wav 형식으로 저장할 수 있게 해줌


RECORDS_DIR = Path('records') # 녹음한 파일을 저장할 폴더의 경로를 변수에 저장

def ensure_records_directory():
    # 레코드 폴더가 없을경우 생성
    if not RECORDS_DIR.exists(): # 폴더가 있는지 없는지 확인
        RECORDS_DIR.mkdir()


def get_current_timestamp(): # 현재 시간을 가져와서 문자열로 변환
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d-%H%M%S')


def record_audio(duration_seconds=5, sample_rate=44100): #녹음 진행 함수
    print('녹음을 시작합니다...') # 녹음 시작 메세지 출력, 기본으로 5초 녹음, 초당 44,100개의 소리 샘플을 받음

    audio = sd.rec(
        int(duration_seconds * sample_rate), 
        samplerate=sample_rate,
        channels=2, #
        dtype='int16'
    )
    sd.wait()
    print('녹음이 완료되었습니다.')

    timestamp = get_current_timestamp()
    filename = RECORDS_DIR / (timestamp + '.wav')
    write(filename, sample_rate, audio) # 실제로 음성녹음된 파일을 저장
    print('파일이 저장되었습니다:', filename)


def extract_date_from_filename(filename):
    try:
        date_part = filename.split('-')[0]
        return datetime.datetime.strptime(date_part, '%Y%m%d')
    except (ValueError, IndexError):
        return None


def list_files_in_date_range(start_date_str, end_date_str):
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')

    print(start_date_str + '부터 ' + end_date_str + '까지의 녹음 파일을 찾는 중입니다...')

    matched_files = []

    for file in RECORDS_DIR.glob('*.wav'): #wav 형식의 파일을 모두 확인
        file_date = extract_date_from_filename(file.name)
        if file_date is None:
            continue

        if start_date <= file_date <= end_date: # 날짜 범위에 포함되는 파일만 리스트에 추가
            matched_files.append((file_date, file.name))

    if not matched_files:
        print('해당 범위에 녹음된 파일이 없습니다.')
        return

    matched_files.sort()

    print('\n총', len(matched_files), '개의 파일이 검색되었습니다:\n')
    for _, filename in matched_files:
        print(filename)


def main():
    ensure_records_directory()
    record_audio(5)

    # ✅ 사용자에게 입력받을 수도 있고, 하드코딩 예시를 줄 수도 있음
    list_files_in_date_range('20250601', '20250630')


if __name__ == '__main__':
    main()
