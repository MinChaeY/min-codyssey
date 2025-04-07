import time
import random  # 센서 값을 무작위로 생성하기 위해 사용


# DummySensor 클래스는 센서 값을 무작위로 생성하여 반환하는 역할을 함
class DummySensor:
    def get_internal_temperature(self):
        return round(random.uniform(18.0, 25.0), 2)

    def get_external_temperature(self):
        return round(random.uniform(-70.0, -10.0), 2)

    def get_internal_humidity(self):
        return round(random.uniform(30.0, 60.0), 2)

    def get_external_illuminance(self):
        return round(random.uniform(100.0, 1000.0), 2)

    def get_internal_co2(self):
        return round(random.uniform(0.02, 0.1), 4)

    def get_internal_oxygen(self):
        return round(random.uniform(19.0, 23.0), 2)


# MissionComputer 클래스는 센서 데이터를 수집하고 출력하는 역할을 담당함
class MissionComputer:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }
        self.ds = DummySensor()

        # 5분 평균을 계산하기 위한 히스토리 저장 공간
        self.history = {key: [] for key in self.env_values}

         # 각 센서 값에 대한 단위 정의
        self.units = {
            'mars_base_internal_temperature': '°C',
            'mars_base_external_temperature': '°C',
            'mars_base_internal_humidity': '%',
            'mars_base_external_illuminance': 'W/m²',
            'mars_base_internal_co2': '%',
            'mars_base_internal_oxygen': '%'
        }

    def get_sensor_data(self):
        start_time = time.time()  # 5분 타이머 시작 시간

        while True:
            # 보너스 과제1: stop.txt 파일을 확인하여 종료 조건을 감지함
            try:
                with open('stop.txt', 'r') as file:
                    stop_signal = file.read().strip()
                    if stop_signal == 'q':
                        print('System stopped...')
                        break
            except FileNotFoundError:
                with open('stop.txt', 'w') as file:
                    file.write('')

            # 현재 센서 값 수집 및 저장
            self.env_values['mars_base_internal_temperature'] = self.ds.get_internal_temperature()
            self.env_values['mars_base_external_temperature'] = self.ds.get_external_temperature()
            self.env_values['mars_base_internal_humidity'] = self.ds.get_internal_humidity()
            self.env_values['mars_base_external_illuminance'] = self.ds.get_external_illuminance()
            self.env_values['mars_base_internal_co2'] = self.ds.get_internal_co2()
            self.env_values['mars_base_internal_oxygen'] = self.ds.get_internal_oxygen()

            # 각 센서 값 히스토리에 추가 (평균 계산용)
            for key in self.env_values:
                self.history[key].append(self.env_values[key])


            # 현재 측정값 출력 (JSON 형태 흉내)
            print('{')
            for key, value in self.env_values.items():
                unit = self.units.get(key, '')  # 단위 가져오기 (없으면 빈 문자열)
                print('  \'{}\': {} {},'.format(key, value, unit))
            print('}')


            # 5분(= 300초) 경과 시 평균값 출력
            elapsed_time = time.time() - start_time
            if elapsed_time >= 300:
                print('\n[5분 평균 환경 정보]')
                for key in self.history:
                    values = self.history[key]
                    if values:  # 값이 존재할 경우 평균 계산
                        avg = round(sum(values) / len(values), 2)
                        unit = self.units.get(key, '')
                        print('  \'{}\': 평균값 = {} {}'.format(key, avg, unit))
                print('--------------------------\n')


                # 평균 출력 후 타이머 및 히스토리 초기화
                start_time = time.time()
                for key in self.history:
                    self.history[key] = []

            # 5초마다 반복
            time.sleep(5)


# MissionComputer 인스턴스를 RunComputer로 생성하고 센서 수집을 시작
RunComputer = MissionComputer()
RunComputer.get_sensor_data()
