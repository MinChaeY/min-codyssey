import os
import csv

#로그파일을 읽어오는 함수.
def read_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            #각 행을 딕셔너리 형식으로 읽어들임
            reader = csv.DictReader(file)
            log_content = [row for row in reader]
        return log_content
    # 파일이 존재하지 않을 경우 예외처리
    except FileNotFoundError as e:
        print(f'파일을 읽는 중 에러가 발생했습니다: {e}')
        # 빈 리스트를 반환
    return []
#파일을 닫는 close 필요, 다만 with open를 쓰면 자동으로 close를 해주긴 함. with만 쓰는 경우에는 close가 필요

def print_log_to_screen(log_entries):
    # 로그 항목을 화면에 출력
    if log_entries:
        for log in log_entries:
            print(f"| {log['timestamp']} | {log['event']} | {log['message']} |")
    else:
        print('로그 파일이 비어 있거나 읽을 수 없습니다.')

def analyze_logs(log_entries):
    accident_logs = []
    accident_cause = ''
# 이건 사고의 원인이 된 요소를 선택해 출력한것, 특정 시간대 이후의 로그를 출력하는 방법도 있음.
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
#다른 로그파일을 받을 경우나 코드를 돌릴 경우에는 정적이기 때문에 다른 로그파일에는 대응이 어렵다. 
#재사용에는 어려움이 따른다는 점이 아쉽다.
#나중에 수정이 필요함. 동적으로 하려면 어떻게 해야할까? 
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
            file.write('로그에서 사고의 명확한 원인을 찾을 수 없었습니다.\n')

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
