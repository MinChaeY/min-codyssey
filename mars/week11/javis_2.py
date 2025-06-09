import datetime  # 날짜와 시간 관련 기능을 제공하는 표준 라이브러리
from pathlib import Path  # 경로 객체를 다루기 위한 표준 라이브러리
import sounddevice as sd  # 오디오 녹음을 위한 외부 라이브러리
# wave 를 사용하여 저장할 수도 있지만 scipy.io.wavfile를 사용할 경우 wave보다 더 간결하고 직관적으로 저장이 가능함
# wave -> 프레임 단위로 데이터를 수동으로 작성
# scipy.io.wavfile 은 NumPy 배열 한 줄로 .wav 파일을 저장함
# 이미 전제조건을 세우고 내부처리를 자동화한 함수이기 때문에 간편한 것.
from scipy.io.wavfile import write  # numpy 배열을 .wav 파일로 저장하는 함수
# whisper 는 소리를 숫자로 변경해주는 모델이며 오디오 파일을 직접 읽지 못함. 그래서 사용을 위해서는 ffmpeg 설치가 필요함
# ffmepg는 오디오 변환 전문 도구임
import whisper  # OpenAI Whisper 모델을 이용한 STT 라이브러리
import csv  # CSV 파일 저장을 위한 표준 라이브러리

# 녹음 파일 및 변환 파일을 저장할 디렉토리 설정
RECORDS_DIR = Path('records')

def ensure_records_directory():
    # records 디렉토리가 존재하지 않을 경우 생성
    if not RECORDS_DIR.exists():
        RECORDS_DIR.mkdir()

def get_current_timestamp():
    # 현재 날짜와 시간을 'YYYYMMDD-HHMMSS' 형식의 문자열로 반환
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d-%H%M%S')

def record_audio(duration_seconds=5, sample_rate=44100):
    # duration_seconds 초 동안 오디오를 녹음하고 .wav 파일로 저장하는 함수
    # sample_rate는 초당 샘플 수를 의미 (44100Hz는 CD 품질)
    print('녹음을 시작합니다...')

    # 지정된 길이(duration_seconds) 동안 stereo(2채널)로 녹음
    audio = sd.rec(
        int(duration_seconds * sample_rate),  # 전체 샘플 수 = 초 * 샘플레이트
        samplerate=sample_rate,
        channels=2,
        dtype='int16'  # 오디오 샘플은 16비트 정수로 저장 (CD 오디오 형식)
    )
    sd.wait()  # 녹음이 끝날 때까지 대기
    print('녹음이 완료되었습니다.')

    # 현재 시간을 기반으로 파일명을 생성하고 records 디렉토리에 저장
    timestamp = get_current_timestamp()
    filename = RECORDS_DIR / (timestamp + '.wav')
    write(filename, sample_rate, audio)
    print('파일이 저장되었습니다:', filename)

    # 녹음된 파일에 대해 STT 변환 수행 및 CSV 저장
    transcribe_audio_to_csv(filename)

def extract_date_from_filename(filename):
    # 파일 이름에서 날짜 부분('YYYYMMDD')만 추출하여 datetime 객체로 반환
    try:
        date_part = filename.split('-')[0]  # 'YYYYMMDD-HHMMSS.wav'에서 날짜 부분만 분리
        return datetime.datetime.strptime(date_part, '%Y%m%d')
    except (ValueError, IndexError):
        # 날짜 형식이 맞지 않거나 '-'가 없는 경우 None 반환
        return None

def list_files_in_date_range(start_date_str, end_date_str):
    # 주어진 날짜 범위(start_date_str ~ end_date_str) 내에 존재하는 녹음 파일 목록 출력
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')

    print(start_date_str + '부터 ' + end_date_str + '까지의 녹음 파일을 찾는 중입니다...')

    matched_files = []

    for file in RECORDS_DIR.glob('*.wav'):  # records 폴더 내 .wav 파일 모두 확인
        file_date = extract_date_from_filename(file.name)
        if file_date is None:
            continue

        if start_date <= file_date <= end_date:
            matched_files.append((file_date, file.name))

    if not matched_files:
        print('해당 범위에 녹음된 파일이 없습니다.')
        return

    matched_files.sort()  # 날짜순 정렬
    print('\n총', len(matched_files), '개의 파일이 검색되었습니다:\n')
    for _, filename in matched_files:
        print(filename)

def transcribe_audio_to_csv(audio_path):
    # Whisper 모델을 이용하여 음성 파일을 텍스트로 변환하고, 구간별 시간과 함께 CSV로 저장
    print('Whisper 모델 로드 중입니다...')
    model = whisper.load_model('base')  # base 모델 로드 (경량, 빠름)

    print('음성을 분석 중입니다...')
    # 한국어로 지정하여 음성 텍스트 변환 수행
    result = model.transcribe(str(audio_path), language='ko')

    segments = result.get('segments', [])
    if not segments:
        print('분석된 문장이 없습니다.')
        return

    # 동일한 파일 이름으로 .csv 확장자를 가지는 파일 생성
    csv_path = Path(audio_path).with_suffix('.csv')

    with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['시작시간', '종료시간', '텍스트'])  # CSV 헤더

        for segment in segments:
            start = format_timestamp(segment['start'])  # 시작 시간 (초 → mm:ss)
            end = format_timestamp(segment['end'])  # 종료 시간 (초 → mm:ss)
            text = segment['text'].strip()
            writer.writerow([start, end, text])  # 시간 + 인식된 텍스트 저장

    print('CSV 파일이 저장되었습니다:', csv_path)

def format_timestamp(seconds):
    # 초 단위 시간을 분:초(mm:ss) 형식 문자열로 변환
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f'{minutes:02}:{secs:02}'

def search_keyword_in_csv(keyword):
    # 모든 CSV 파일을 검색하여 키워드가 포함된 텍스트가 있는 줄을 출력
    print(f'"{keyword}" 키워드로 CSV 파일을 검색 중입니다...')
    found = False

    for file in RECORDS_DIR.glob('*.csv'):
        with open(file, encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # 첫 줄(헤더) 건너뜀

            for row in reader:
                if keyword in row[2]:  # 세 번째 열(텍스트)에 키워드가 포함되어 있는지 확인
                    print(f'[{file.name}] {row[0]}~{row[1]}: {row[2]}')
                    found = True

    if not found:
        print('해당 키워드가 포함된 내용이 없습니다.')

def main():
    # 전체 프로그램 실행의 진입점
    ensure_records_directory()  # 저장 폴더가 있는지 확인하고 없으면 생성
    record_audio(5)  # 기본 5초간 녹음 수행
    list_files_in_date_range('20250601', '20250630')  # 6월 내 파일 검색

    # 사용자로부터 검색할 키워드 입력받기
    keyword = input('검색할 키워드를 입력하세요: ').strip()
    if keyword:
        search_keyword_in_csv(keyword)  # 키워드가 입력되면 CSV들에서 검색 수행
    else:
        print('검색어가 입력되지 않았습니다.')

# 이 파일이 직접 실행될 경우 main() 실행
if __name__ == '__main__':
    main()
