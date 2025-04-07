import random

class DummySensor:
    def __init__(self):
        self.env_values = {
            'mars_base_internal_temperature': (0.0, "°C"),
            'mars_base_external_temperature': (0.0, "°C"),
            'mars_base_internal_humidity': (0.0, "%"),
            'mars_base_external_illuminance': (0.0, "lx"),
            'mars_base_internal_co2': (0.0, "%"),
            'mars_base_internal_oxygen': (0.0, "%")
        }

    def set_env(self):
        """랜덤 환경 값을 생성하여 딕셔너리에 저장"""
        self.env_values['mars_base_internal_temperature'] = (round(random.uniform(18, 30), 2), "°C")
        self.env_values['mars_base_external_temperature'] = (round(random.uniform(0, 21), 2), "°C")
        self.env_values['mars_base_internal_humidity'] = (round(random.uniform(50, 60), 2), "%")
        self.env_values['mars_base_external_illuminance'] = (round(random.uniform(500, 715), 2), "W/m²")
        self.env_values['mars_base_internal_co2'] = (round(random.uniform(0.02, 0.1), 4), "%")
        self.env_values['mars_base_internal_oxygen'] = (round(random.uniform(4, 7), 2), "%")

        # 이상값 감지 (예: 산소 농도 경고)
        if not (4 <= self.env_values['mars_base_internal_oxygen'][0] <= 7):
            print("⚠️ 경고: 내부 산소 농도가 비정상적입니다!")

    def get_env(self, start_time):
        """환경 값을 로그 파일에 기록하고 반환"""
        # 입력 유효성 검사
        if not (len(start_time) == 12 and start_time.isdigit()):
            print("❌ 잘못된 형식입니다. YYYYMMDDHHMM 형식으로 입력하세요.")
            exit()

        try:
            year = int(start_time[:4])
            month = int(start_time[4:6])
            day = int(start_time[6:8])
            hour = int(start_time[8:10])
            minute = int(start_time[10:12])
        except ValueError:
            print("❌ 잘못된 입력입니다. 숫자만 포함된 YYYYMMDDHHMM 형식으로 입력하세요.")
            exit()

        print(f"Entered time: {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")

        log_file_path = "mars_mission_log.txt"

        try:
            with open(log_file_path, "a") as log_file:
                log_file.write(f"\n[{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}]\n")
                for key, (value, unit) in self.env_values.items():
                    log_file.write(f"{key}: {value} {unit}\n")
                log_file.write("=" * 40 + "\n")  # 구분선 추가
        except Exception as e:
            print(f"❌ 로그 파일 기록 중 오류 발생: {e}")

        return self.env_values

# 실행 코드
ds = DummySensor()

current_time_input = input("현재 시간을 YYYYMMDDHHMM 포맷으로 입력하시오: ")
ds.set_env()
env_data = ds.get_env(current_time_input)

print("\n🔹 Generated Environmental Data:")
for key, (value, unit) in env_data.items():
    print(f"{key}: {value} {unit}")
