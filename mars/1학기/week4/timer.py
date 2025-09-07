import time

class SimpleTimer:
    def __init__(self):
        self.start_time = time.time()  # 타이머 시작 시간을 기록
        self.elapsed_time = 0  # 경과 시간 초기화

    def check_and_log(self):
        """경과 시간이 5분 이상이면 로그 기록 후 시간 초기화"""
        # 현재 시간을 구해서 경과 시간 계산 (초 단위)
        current_time = time.time()
        self.elapsed_time = current_time - self.start_time
        
        # 경과 시간이 5분 이상일 때
        if self.elapsed_time >= 300:  # 5분(300초)
            self.log()
            self.start_time = current_time  # 타이머 초기화

    def log(self):
        """경과 시간 로그 출력"""
        minutes = self.elapsed_time // 60
        seconds = self.elapsed_time % 60
        print(f"로그 기록: {int(minutes)}분 {int(seconds)}초 경과")

# 예시 사용
timer = SimpleTimer()

# 주기적으로 경과 시간을 체크하여 5분마다 로그 기록
while True:
    timer.check_and_log()  # 5분마다 로그 체크
    time.sleep(1)  # 1초씩 대기
