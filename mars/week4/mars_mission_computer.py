import random

class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': 0.0,
            'mars_base_external_temperature': 0.0,
            'mars_base_internal_humidity': 0.0,
            'mars_base_external_illuminance': 0.0,
            'mars_base_internal_co2': 0.0,
            'mars_base_internal_oxygen': 0.0
        }

    def set_env(self):
        # 환경 변수 랜덤 값 생성
        self.env_values['mars_base_internal_temperature'] = round(random.uniform(18, 30), 2)
        self.env_values['mars_base_external_temperature'] = round(random.uniform(0, 21), 2)
        self.env_values['mars_base_internal_humidity'] = round(random.uniform(50, 60), 2)
        self.env_values['mars_base_external_illuminance'] = round(random.uniform(500, 715), 2)
        self.env_values['mars_base_internal_co2'] = round(random.uniform(0.02, 0.1), 4)
        self.env_values['mars_base_internal_oxygen'] = round(random.uniform(4, 7), 2)

    def get_env(self, start_time):
        # 입력된 시간을 변환하여 년, 월, 일, 시, 분으로 분리
        year = int(start_time[:4])
        month = int(start_time[4:6])
        day = int(start_time[6:8])
        hour = int(start_time[8:10])
        minute = int(start_time[10:12])

        # 변환된 시간 출력
        print(f"Entered time: {year}-{month}-{day} {hour}:{minute}")

        # 입력된 시간 (년-월-일 시:분 형식) 그대로 출력
        current_time_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"

        # 로그 파일 경로 설정 (현재 디렉토리에 mars_mission_log.txt로 저장)
        log_file_path = "mars_mission_log.txt"

        # 로그 파일에 기록
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{current_time_str} - ")
            for key, value in self.env_values.items():
                log_file.write(f"{key}: {value}, ")
            log_file.write("\n")

        return self.env_values

# 인스턴스 생성
ds = DummySensor()

# 실행자가 현재 시간을 입력받음 (예: 202503311236 형식으로 입력)
current_time_input = input("Enter the current time in YYYYMMDDHHMM format: ")

# set_env()와 get_env() 호출하여 값 확인하고 로그 남기기
ds.set_env()
env_data = ds.get_env(current_time_input)

# 확인용 출력
print("Generated Environmental Data:")
for key, value in env_data.items():
    print(f"{key}: {value}")
