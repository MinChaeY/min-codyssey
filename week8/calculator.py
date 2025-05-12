import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt

MAX_VALUE = 1e160  # 아이폰 계산기의 최대 계산 숫자 근사치

class Calculator:
    def __init__(self):
        self.reset()  # 계산기 상태 초기화

    def reset(self):
        self.current_input = ""  # 현재 입력 중인 문자열 수식
        self.result = None       # 계산 결과 저장

    def input_number(self, num):
        # 숫자 또는 소수점 입력 처리
        if self.current_input == "0" and num != ".":
            self.current_input = num
        elif num == ".":
            if "." in self.get_last_number():  # 소수점 중복 방지
                return
            self.current_input += num
        else:
            self.current_input += num

    def input_operator(self, op):
        # 수식의 마지막 문자가 연산자가 아니면 연산자 추가
        if self.current_input and self.current_input[-1] not in "+-*/":
            self.current_input += op

    # 연산자 입력용 헬퍼 메서드들
    def add(self):
        self.input_operator("+")

    def subtract(self):
        self.input_operator("-")

    def multiply(self):
        self.input_operator("×")

    def divide(self):
        self.input_operator("÷")

    def toggle_sign(self):
        # 현재 입력값의 마지막 숫자 부호를 반전
        if not self.current_input:
            return
        tokens = list(self.current_input)
        i = len(tokens) - 1
        while i >= 0 and (tokens[i].isdigit() or tokens[i] == "."):
            i -= 1
        if i >= 0 and tokens[i] == "-":
            del tokens[i]  # 기존 - 부호 제거
        else:
            tokens.insert(i + 1, "-")  # - 부호 삽입
        self.current_input = "".join(tokens)

    def percent(self):
        # 입력값을 100으로 나눈 결과로 설정
        try:
            value = eval(self.current_input)
            value /= 100
            self.current_input = str(value)
        except:
            self.current_input = "Error"

    def equal(self):
        # 수식 계산 처리 및 결과 반환
        try:
            result = eval(self.current_input.replace("×", "*").replace("÷", "/"))
            if abs(result) > MAX_VALUE:  # MAX_VALUE는 정의 필요
                raise OverflowError
            rounded_result = round(result, 6)
            self.result = str(rounded_result)
        except ZeroDivisionError:
            self.result = "Error"
        except OverflowError:
            self.result = "Overflow"
        except:
            self.result = "Error"
        self.current_input = self.result
        return self.result

    def get_last_number(self):
        # 마지막 숫자 추출 (소수점 중복 검사용)
        for op in "+-*/":
            if op in self.current_input:
                return self.current_input.split(op)[-1]
        return self.current_input

    def update_display(self, text):
        # 글자 수에 따라 폰트 크기 조절
        font_size = 64
        if len(text) > 9:
            font_size = 48
        if len(text) > 15:
            font_size = 32
        self.display.setStyleSheet(self.get_display_style(font_size))
        self.display.setText(text)

    def get_display_style(self, size):
        # QLabel용 스타일 문자열 생성
        return f"""
            color: white;
            font-size: {size}px;
            padding: 30px 10px 10px 10px;
            font-family: 'Arial';
        """


class IPhoneCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Calculator")
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(390, 650)
        self.calculator = Calculator()  # 계산 로직 객체
        self.init_ui()

    def init_ui(self):
        # 디스플레이 영역 생성
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet(self.calculator.get_display_style(64))

        # 버튼 정의 (5행 구성)
        buttons = [
            ["AC", "+/-", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "="]
        ]

        grid = QGridLayout()
        grid.setSpacing(10)

        for row, line in enumerate(buttons):
            col = 0
            for btn_text in line:
                button = QPushButton(btn_text)
                if btn_text == "0":
                    # '0' 버튼은 2칸 차지
                    button.setFixedSize(170, 80)
                    grid.addWidget(button, row + 1, 0, 1, 2)
                    col += 1
                else:
                    button.setFixedSize(80, 80)
                    grid.addWidget(button, row + 1, col if btn_text != "0" else 2, 1, 1)

                # 버튼 스타일 설정
                if btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet(self.style_function_btn())
                elif btn_text in ["+", "-", "×", "÷", "="]:
                    button.setStyleSheet(self.style_operator_btn())
                else:
                    button.setStyleSheet(self.style_number_btn())

                # 버튼 클릭 시 연결 함수 지정
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

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.display)
        layout.addLayout(grid)
        self.setLayout(layout)

    # 입력 처리 함수들 (버튼 연결용)
    def input_number(self, num):
        self.calculator.input_number(num)
        self.update_display(self.calculator.current_input)

    def input_operator(self, op):
        self.calculator.input_operator(self.convert_operator(op))
        self.update_display(self.calculator.current_input)

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
        # GUI 기호를 파이썬 연산 기호로 변환
        return {
            "×": "*",
            "÷": "/"
        }.get(op, op)

    def update_display(self, text):
        # 디스플레이 업데이트 (글자 수에 따라 폰트 조정)
        font_size = 64
        if len(text) > 9:
            font_size = 48
        if len(text) > 15:
            font_size = 32
        self.display.setStyleSheet(self.calculator.get_display_style(font_size))
        self.display.setText(text)

    # 버튼 스타일 정의 함수들
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
    # PyQt5 애플리케이션 실행부
    app = QApplication(sys.argv)
    window = IPhoneCalculator()
    window.show()
    sys.exit(app.exec_())
