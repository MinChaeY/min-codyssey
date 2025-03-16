import os
import csv

def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            log_content = [row for row in reader]
        return log_content
    except FileNotFoundError as e:
        print(f'파일을 읽는 중 에러가 발생했습니다: {e}')
    return []


def print_log_to_screen(log_entries):
    # 로그 항목을 화면에 출력
    if log_entries:
        print('| 타임스탬프 | 이벤트 | 메시지 |')
        print('|-----------|--------|---------|')
        for log in log_entries:
            print(f"| {log['timestamp']} | {log['event']} | {log['message']} |")
    else:
        print("로그 파일이 비어 있거나 읽을 수 없습니다.")

def analyze_logs(log_entries):
    accident_logs = []
    accident_cause = ''

    for entry in log_entries:
        # 로그 항목이 'Oxygen tank'를 포함하는지 확인
        if 'Oxygen tank' in entry['message']:
            accident_logs.append(entry)
            if 'unstable' in entry['message']:
                accident_cause = '산소 탱크가 불안정합니다.'
            if 'explosion' in entry['message']:
                accident_cause = '불안정한 산소 탱크에 폭발이 발생하여 화성 기지에 피해를 일으켰습니다.'

    return accident_logs, accident_cause

# Markdown 보고서 작성 함수
def create_report(accident_logs, accident_cause, output_file):
    with open(output_file, mode='w', encoding='utf-8') as file:
        file.write('# 로그 분석 보고서\n\n')
        file.write('## 개요\n')
        file.write('이 보고서는 2023년 8월 27일 임무 중 발생한 로그를 분석한 결과입니다. ')
        file.write('임무는 성공적으로 마무리하였으나, 산소 탱크에서 문제가 발생한 것으로 확인됩니다. \n\n')

        file.write('## 세부 사항 \n')
        file.write('로그에서 사고는 임무가 완료된 후 발생한 것으로 나타났습니다.\n')
        file.write('다음은 산소 탱크와 관련된 이벤트입니다:\n\n')

        file.write('| 타임스탬프 | 이벤트 | 메시지 |\n')
        file.write('|-----------|-------|---------|\n')
        for log in accident_logs:
            file.write(f"| {log['timestamp']} | {log['event']} | {log['message']} |\n")

        file.write('\n## 원인 분석\n')
        if accident_cause:
            file.write(f'사고의 원인은 다음과 같을 가능성이 있습니다: **{accident_cause}**.\n')
        else:
            file.write("로그에서 사고의 명확한 원인을 찾을 수 없었습니다.\n")

        file.write('\n## 결론\n')
        file.write('임무는 성공적으로 완료되었지만, 산소 탱크의 폭발로 센터와 임무 통제 시스템의 전원이 꺼졌습니다.\n')
        file.write('추후에 사고를 방지하기 위해 추가적인 조사가 필요합니다.\n')




# 메인 함수
def main():
    # 현재 스크립트의 디렉토리 경로를 가져옴
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_file = os.path.join(script_dir, 'mission_computer_main.log')  # 로그 파일 경로 설정
    
    # 보고서 파일을 main.py와 동일한 위치에 생성
    output_file = os.path.join(script_dir, 'log_analysis.md')

    # 1. 로그 파일 읽기
    log_entries = read_log_file(log_file)

     # 2. 화면에 로그 출력
    print_log_to_screen(log_entries)

    if not log_entries:
        print("로그 파일이 비어 있거나 읽을 수 없습니다.")
        return

    # 2. 사고 로그 분석
    accident_logs, accident_cause = analyze_logs(log_entries)

    # 3. 보고서 생성
    create_report(accident_logs, accident_cause, output_file)
    print(f"Report created: {output_file}")

if __name__ == "__main__":
    main()
