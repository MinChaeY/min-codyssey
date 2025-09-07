import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt

MAX_VALUE = 1e160  # 아이폰 계산기의 최대 계산 숫자 근사치

class Calculator:
    def __init__(self):
        self.reset()  # 생성자에서 계산기 상태 초기화

#계산기 상태를 초기화, self.calculator.reset() 호출함
    def reset(self):
        self.current_input = ""  # 현재까지 입력된 수식 (문자열 형태)
        self.result = None       # 최종 계산 결과 저장

    def input_number(self, num):
        # 숫자 또는 소수점 입력 처리 메서드
        # 현재 입력값이 "0"일 경우 새로운 숫자로 대체
        if self.current_input == "0" and num != ".":
            self.current_input = num
        elif num == ".":
            # 이미 소수점이 있으면 무시
            if "." in self.get_last_number():
                return
            self.current_input += num  # 소수점 추가
        else:
            self.current_input += num  # 일반 숫자 추가

    def input_operator(self, op):
        # 수식의 마지막 문자가 연산자가 아닐 때만 연산자 추가
        if self.current_input and self.current_input[-1] not in "+-*/":
            self.current_input += op

    # 각 연산자에 대한 헬퍼 메서드들
    #중복된 로직들을 간단하게 호출 할 수 있도록 만듦
    #버튼을 늘렀을때 연결된 input_operator 호출, 내부에서 self~ 실행. 
    #UI 버튼과 계산 로직을 분리하기 위해 나눠씀
    def add(self):
        self.input_operator("+")

    def subtract(self):
        self.input_operator("-")

    def multiply(self):
        self.input_operator("×")  # 사용자 인터페이스용 기호 계산용 기호는 아님.

    def divide(self):
        self.input_operator("÷")

    def toggle_sign(self):
        # 현재 입력의 마지막 숫자 앞에 부호(-) 추가 또는 제거
        if not self.current_input:
            return
        tokens = list(self.current_input)  # 문자 리스트로 변환
        i = len(tokens) - 1
        # 마지막 숫자의 시작 위치 탐색
        while i >= 0 and (tokens[i].isdigit() or tokens[i] == "."):
            i -= 1
        if i >= 0 and tokens[i] == "-": #이미 부호가 있을 경우,
            del tokens[i]  # 기존 부호 제거
        else:
            tokens.insert(i + 1, "-")  # 새로운 부호 삽입
        self.current_input = "".join(tokens)

    def percent(self):
        # eval() 로 현재 수식을 평가함. -> 문자열을 가져와서 실수로 변환하여 실제 계산에 사용할 수 있도록 함.
        # 현재 결과에 /100 울 적용한 후 문자열로 변환하여 다시 cuerrent_input에 저장함
        try:
            value = eval(self.current_input)  # 문자열 수식 평가
            value /= 100
            self.current_input = str(value)  # 다시 문자열로 저장
        except:
            self.current_input = "Error"  # 계산 오류 시 에러 표시

    def equal(self):
        # 수식 계산 수행 후 결과 반환
        try:
            # 사용자 입력 기호를 Python 연산자로 변환
            result = eval(self.current_input.replace("×", "*").replace("÷", "/"))
            if abs(result) > MAX_VALUE:
                raise OverflowError  # 너무 큰 값은 Overflow 처리
            rounded_result = round(result, 6)  # 소수점 6자리 반올림
            self.result = str(rounded_result)
        except ZeroDivisionError:
            self.result = "0으로 나눌 수 없습니다."  # 0으로 나누면 에러
        except OverflowError:
            self.result = "Overflow"  # Overflow 처리
        except:
            self.result = "Error"  # 그 외 에러
        self.current_input = self.result  # 결과를 다음 입력값으로 설정
        return self.result

    def get_last_number(self):
        # 현재 입력된 수식에서 마지막 숫자만 반환
        for op in "+-*/":
            if op in self.current_input:
                return self.current_input.split(op)[-1]  # 마지막 피연산자
        return self.current_input

    def update_display(self, text):
        # 글자 수에 따라 폰트 크기를 자동 조정하고 디스플레이 업데이트
        font_size = 64
        if len(text) > 9:
            font_size = 48
        if len(text) > 15:
            font_size = 32
        self.display.setStyleSheet(self.get_display_style(font_size))
        self.display.setText(text)

    def get_display_style(self, size):
        # 폰트 스타일 문자열 반환
        return f"""
            color: white;
            font-size: {size}px;
            padding: 30px 10px 10px 10px;
            font-family: 'Arial';
        """


class IPhoneCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Calculator")  # 윈도우 제목
        self.setStyleSheet("background-color: black;")  # 배경색 설정
        self.setFixedSize(390, 650)  # iPhone 화면 비율 크기
        self.calculator = Calculator()  # 계산 로직 객체 생성
        self.init_ui()  # UI 초기화

    def init_ui(self):
        # 디스플레이 라벨 생성 및 초기 설정
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet(self.calculator.get_display_style(64))

        # 계산기 버튼 배열 정의
        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        grid = QGridLayout()  # 버튼 레이아웃 설정
        grid.setSpacing(10)

        for row, line in enumerate(buttons):
            col = 0
            for btn_text in line:
                button = QPushButton(btn_text)
                if btn_text == "0":
                    # 0 버튼은 너비를 두 칸 차지
                    button.setFixedSize(170, 80)
                    grid.addWidget(button, row + 1, 0, 1, 2)
                    col += 1
                else:
                    button.setFixedSize(80, 80)
                    grid.addWidget(button, row + 1, col if btn_text != "0" else 2, 1, 1)

                # 버튼 색상 및 스타일 분기 설정
                if btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet(self.style_function_btn())
                elif btn_text in ["+", "-", "×", "÷", "="]:
                    button.setStyleSheet(self.style_operator_btn())
                else:
                    button.setStyleSheet(self.style_number_btn())

                # 버튼 동작 연결
                if btn_text.isdigit() or btn_text == ".":
                    button.clicked.connect(lambda checked, text=btn_text: self.input_number(text))
                elif btn_text in ["+", "-", "×", "÷"]:
                    button.clicked.connect(lambda checked, op=btn_text: self.input_operator(op))
                elif btn_text == "=":
                    button.clicked.connect(self.calculate_result)
                elif btn_text == "AC":
                    button.clicked.connect(self.clear_display)
                elif btn_text == "+/-":
                    button.clicked.connect(self.toggle_sign)
                elif btn_text == "%":
                    button.clicked.connect(self.percent)

                col += 1

        # 전체 레이아웃 구성
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.display)
        layout.addLayout(grid)
        self.setLayout(layout)

    # 숫자 버튼 클릭 시 호출됨
    def input_number(self, num):
        self.calculator.input_number(num)
        self.update_display(self.calculator.current_input)

    # 연산자 버튼 클릭 시 호출됨
    # 클래스와 로직을 연결하기 위한 중간계층임
    # ui 버튼 클릭 -> IPhoneCalculator 함수 -> Calculator 호출 -> 결과 받아와서 디스플레이를 업데이트
    def input_operator(self, op):
        self.calculator.input_operator(self.convert_operator(op))
        self.update_display(self.calculator.current_input)
# 
    def toggle_sign(self):
        self.calculator.toggle_sign()
        self.update_display(self.calculator.current_input)

    def percent(self):
        self.calculator.percent()
        self.update_display(self.calculator.current_input)

    def calculate_result(self):
        result = self.calculator.equal()
        self.update_display(result)

    def clear_display(self):
        self.calculator.reset()
        self.update_display("0")

    def convert_operator(self, op):
        # 사용자 입력 기호를 내부 연산자 기호로 변환
        return {
            "×": "*",
            "÷": "/"
        }.get(op, op)

    def update_display(self, text):
        # 디스플레이에 값 출력 및 폰트 조정
        font_size = 64
        if len(text) > 9:
            font_size = 48
        if len(text) > 15:
            font_size = 32
        self.display.setStyleSheet(self.calculator.get_display_style(font_size))
        self.display.setText(text)

    # 숫자 버튼 스타일 설정
    def style_number_btn(self):
        return """
            QPushButton {
                background-color: #505050;
                color: white;
                border: none;
                border-radius: 40px;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Arial';
            }
            QPushButton:pressed {
                background-color: #707070;
            }
        """

    # 연산자 버튼 스타일 설정
    def style_operator_btn(self):
        return """
            QPushButton {
                background-color: #FF9500;
                color: white;
                border: none;
                border-radius: 40px;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Arial';
            }
            QPushButton:pressed {
                background-color: #CC7A00;
            }
        """

    # 기능 버튼 스타일 설정 (AC, +/- 등)
    def style_function_btn(self):
        return """
            QPushButton {
                background-color: #D4D4D2;
                color: black;
                border: none;
                border-radius: 40px;
                font-size: 28px;
                font-family: 'Arial';
            }
            QPushButton:pressed {
                background-color: #BFBFBD;
            }
        """


if __name__ == "__main__":
    # PyQt 애플리케이션 실행부
    app = QApplication(sys.argv)
    window = IPhoneCalculator()  # GUI 창 생성
    window.show()  # 창 표시
    sys.exit(app.exec_())  # 이벤트 루프 실행
