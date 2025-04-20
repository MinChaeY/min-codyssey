import platform
import os
import psutil

class MissionComputer:
    def __init__(self):
        self.info_settings, self.load_settings = self.load_settings()

        # 시스템 정보 항목을 미리 정의한 딕셔너리로 매핑
        self.info_map = {
            'operating_system': lambda: platform.system(),
            'os_version': lambda: platform.version(),
            'cpu_type': lambda: platform.processor(),
            'cpu_cores': lambda: os.cpu_count(),
            'memory_size': self.get_memory_size,
            'hostname': lambda: platform.node(),
            'gpu_memory': self.get_gpu_memory  # 예시로 추가
        }

        # 부하 정보 항목도 미리 정의한 딕셔너리로 매핑
        self.load_map = {
            'cpu': lambda: f"{psutil.cpu_percent(interval=1)} %",
            'memory': lambda: f"{psutil.virtual_memory().percent} %",
        }

    def load_settings(self):
        info_keys = []
        load_keys = []

        try:
            with open('setting.txt', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('info_'):
                        info_keys.append(line[5:])  # 'info_' 제거
                    elif line.startswith('load_'):
                        load_keys.append(line[5:])  # 'load_' 제거
        except FileNotFoundError:
            print("setting.txt 파일이 없습니다. 기본값으로 실행됩니다.")
        return info_keys, load_keys

    def get_memory_size(self):
        try:
            mem = psutil.virtual_memory().total
            return f'{round(mem / (1024**3), 2)} GB'
        except:
            return '알 수 없음'

    def get_gpu_memory(self):
        # 실제 GPU 정보 가져오려면 nvidia-smi나 GPUtil 필요
        return 'N/A (추후 구현)'

    def get_mission_computer_info(self):
        print('\n[미션 컴퓨터 시스템 정보]')
        print('{')
        for i, key in enumerate(self.info_settings):
            value = self.info_map.get(key, lambda: '알 수 없음')()
            comma = ',' if i < len(self.info_settings) - 1 else ''
            print(f"  '{key}': {value}{comma}")
        print('}')

    def get_mission_computer_load(self):
        print('\n[미션 컴퓨터 실시간 부하]')
        print('{')
        for i, key in enumerate(self.load_settings):
            value = self.load_map.get(key, lambda: '알 수 없음')()
            comma = ',' if i < len(self.load_settings) - 1 else ''
            print(f"  '{key}_usage': {value}{comma}")
        print('}')


# 실행 예시
RunComputer = MissionComputer()
RunComputer.get_mission_computer_info()
RunComputer.get_mission_computer_load()
