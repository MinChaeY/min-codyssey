import random
import time
import platform
import os
import psutil

# DummySensor 클래스는 랜덤으로 환경 데이터를 생성하는 클래스- 저번 문제의 코드
class DummySensor:
    def get_internal_temperature(self):
        # 내부 온도는 18도에서 25도 사이의 랜덤 값으로 반환
        return round(random.uniform(18.0, 25.0), 2)

    def get_external_temperature(self):
        # 외부 온도는 -70도에서 -10도 사이의 랜덤 값으로 반환
        return round(random.uniform(-70.0, -10.0), 2)

    def get_internal_humidity(self):
        # 내부 습도는 30%에서 60% 사이의 랜덤 값으로 반환
        return round(random.uniform(30.0, 60.0), 2)

    def get_external_illuminance(self):
        # 외부 조도는 100에서 1000 사이의 랜덤 값으로 반환
        return round(random.uniform(100.0, 1000.0), 2)

    def get_internal_co2(self):
        # 내부 CO2 농도는 0.02%에서 0.1% 사이의 랜덤 값으로 반환
        return round(random.uniform(0.02, 0.1), 4)

    def get_internal_oxygen(self):
        # 내부 산소 농도는 19%에서 23% 사이의 랜덤 값으로 반환
        return round(random.uniform(19.0, 23.0), 2)


# MissionComputer 클래스는 환경 데이터 수집, 시스템 정보, 부하 정보를 관리하는 클래스
class MissionComputer:
    def __init__(self):
        # 환경 값 초기화. 예시로 환경 변수들을 설정
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        
        # DummySensor 객체를 생성하여 환경 데이터를 가져오는 데 사용
        self.ds = DummySensor()
        
        # 각 환경 변수의 데이터를 저장할 기록 용 리스트 초기화
        self.history = {key: [] for key in self.env_values}
        
        # 각 환경 변수의 단위 설정
        self.units = {
            'mars_base_internal_temperature': '°C',
            'mars_base_external_temperature': '°C',
            'mars_base_internal_humidity': '%',
            'mars_base_external_illuminance': 'W/m²',
            'mars_base_internal_co2': '%',
            'mars_base_internal_oxygen': '%'
        }
        
        # 시스템 정보 항목을 설정 파일에서 읽어오거나 기본값 사용
        self.info_keys = self.load_info_settings()

    def load_info_settings(self):
        """setting.txt에서 시스템 정보 항목을 읽어옴
        기본 항목을 설정 파일에 기록된 항목을 따라 읽고,
        파일이 없으면 기본 항목을 사용함
        """
        default_keys = ['operating_system', 'os_version', 'cpu_type', 'cpu_cores', 'memory_size']
        try:
            # 설정 파일 읽기
            with open('setting.txt', 'r') as f:
                lines = f.read().splitlines()
                return [line.strip() for line in lines if line.strip() in default_keys]
        except FileNotFoundError:
            # 설정 파일이 없으면 기본값을 사용
            return default_keys

    def get_sensor_data(self):
        """환경 데이터를 주기적으로 수집하고 출력
        'stop.txt' 파일에 'q'가 있으면 시스템을 종료하고, 그렇지 않으면 5초마다 환경 데이터를 출력
        """
        start_time = time.time()

        # 무한 루프를 통해 환경 데이터를 계속해서 갱신하고 출력
        while True:
            try:
                # stop.txt 파일을 읽어 종료 신호를 확인
                with open('stop.txt', 'r') as file:
                    stop_signal = file.read().strip()
                    if stop_signal == 'q':  # 'q'가 있으면 시스템 종료
                        print('System stopped...')
                        break
            except FileNotFoundError:
                # stop.txt 파일이 없으면 빈 파일을 새로 생성
                with open('stop.txt', 'w') as file:
                    file.write('')

            # DummySensor로부터 새로운 환경 데이터 값을 가져옴.
            self.env_values['mars_base_internal_temperature'] = self.ds.get_internal_temperature()
            self.env_values['mars_base_external_temperature'] = self.ds.get_external_temperature()
            self.env_values['mars_base_internal_humidity'] = self.ds.get_internal_humidity()
            self.env_values['mars_base_external_illuminance'] = self.ds.get_external_illuminance()
            self.env_values['mars_base_internal_co2'] = self.ds.get_internal_co2()
            self.env_values['mars_base_internal_oxygen'] = self.ds.get_internal_oxygen()

            # 데이터를 기록 리스트에 추가
            for key in self.env_values:
                self.history[key].append(self.env_values[key])

            # 환경 데이터를 출력함
            print('{')
            for key in self.env_values:
                unit = self.units.get(key, '')  # 단위 설정
                print(f'  \'{key}\': {self.env_values[key]} {unit},')
            print('}')

            # 5분 단위로 평균값을 출력
            elapsed_time = time.time() - start_time
            if elapsed_time >= 300:  # 5분(300초)이 경과하면 평균값을 출력
                print('\n[5분 평균 환경 정보]')
                for key in self.env_values:
                    values = self.history[key]
                    if values:  # 기록된 값이 있을 경우에만 평균값을 계산
                        avg = round(sum(values) / len(values), 2)
                        unit = self.units.get(key, '')
                        print(f'  \'{key}\': 평균값 = {avg} {unit}')
                print('--------------------------\n')

                # 5분 후에 타이머 초기화하고 기록된 값을 초기화
                start_time = time.time()
                for key in self.history:
                    self.history[key] = []

            # 5초마다 데이터를 갱신
            time.sleep(5)

    def get_mission_computer_info(self):
        """미션 컴퓨터의 시스템 정보를 출력합니다.
        운영 체제, CPU 정보, 메모리 크기 등의 시스템 정보를 출력
        """
        try:
            # 시스템 정보 가져오기
            info = {
                'operating_system': platform.system(),
                'os_version': platform.version(),
                'cpu_type': platform.processor(),
                'cpu_cores': os.cpu_count(),
                'memory_size': self.get_memory_size()
            }
            print('\n[미션 컴퓨터 시스템 정보]')
            print('{')
            for i, key in enumerate(self.info_keys):
                end_char = ',' if i < len(self.info_keys) - 1 else ''  # 마지막 항목은 쉼표 없이 출력하도록 함
                print(f"  '{key}': {info[key]}{end_char}")
            print('}')
        except Exception as e:
            print('시스템 정보를 가져오는 중 오류 발생:', e)

    def get_memory_size(self):
        """시스템 메모리 크기를 반환하는 함수
        메모리 크기를 GB 단위로 반환
        """
        try:
            # 시스템 메모리 정보를 psutil을 이용해 가져옴
            mem = psutil.virtual_memory().total
            return f'{round(mem / (1024**3), 2)} GB'  # GB 단위로 반환
        except Exception:
            return '알 수 없음'

    def get_mission_computer_load(self):
        """미션 컴퓨터의 CPU와 메모리 사용량을 실시간으로 출력 """
        try:
            # CPU 사용률 측정
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = round(memory.percent, 2)  # 메모리 사용률

            print('\n[미션 컴퓨터 실시간 부하]')
            print('{')
            print(f'  \'cpu_usage_percent\': {cpu_usage} %,')
            print(f'  \'memory_usage_percent\': {memory_usage} %')
            print('}')
        except Exception as e:
            print('부하 정보를 가져오는 중 오류 발생:', e)


# 실행 예시
RunComputer = MissionComputer()  # MissionComputer 객체 생성
RunComputer.get_mission_computer_info()  # 미션 컴퓨터 정보 출력
RunComputer.get_mission_computer_load()  # 미션 컴퓨터 부하 정보 출력
# RunComputer.get_sensor_data()  # 환경 데이터 주기적으로 출력 (필요시 실행)