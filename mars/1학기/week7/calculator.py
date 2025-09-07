import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout
from PyQt5.QtCore import Qt

class IPhoneCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iPhone Calculator")
        self.setStyleSheet("background-color: black;")
        self.setFixedSize(390, 650)
        self.current_input = ""
        self.init_ui()

    def init_ui(self):
        self.display = QLabel("0")
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet("""
            color: white;
            font-size: 64px;
            padding: 30px 10px 10px 10px;
            font-family: 'Arial';
        """)

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
                    button.setFixedSize(170, 80)
                    grid.addWidget(button, row + 1, 0, 1, 2)
                    col += 1
                else:
                    button.setFixedSize(80, 80)
                    grid.addWidget(button, row + 1, col if btn_text != "0" else 2, 1, 1)

                # 스타일 설정
                if btn_text in ["AC", "+/-", "%"]:
                    button.setStyleSheet(self.style_function_btn())
                elif btn_text in ["+", "-", "×", "÷", "="]:
                    button.setStyleSheet(self.style_operator_btn())
                else:
                    button.setStyleSheet(self.style_number_btn())

                # 기능 연결
                if btn_text.isdigit() or btn_text == ".":
                    button.clicked.connect(lambda checked, text=btn_text: self.input_number(text))
                elif btn_text in ["+", "-", "×", "÷"]:
                    button.clicked.connect(lambda checked, op=btn_text: self.input_operator(op))
                elif btn_text == "=":
                    button.clicked.connect(self.calculate_result)
                elif btn_text == "AC":
                    button.clicked.connect(self.clear_display)

                col += 1

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.display)
        layout.addLayout(grid)
        self.setLayout(layout)

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

    def input_number(self, num):
        if self.display.text() == "0":
            self.current_input = num
        else:
            self.current_input += num
        self.display.setText(self.current_input)

    def input_operator(self, op):
        if self.current_input and self.current_input[-1] not in "+-*/":
            self.current_input += self.convert_operator(op)
            self.display.setText(self.current_input)

    def convert_operator(self, op):
        return {
            "×": "*",
            "÷": "/"
        }.get(op, op)

    def calculate_result(self):
        try:
            result = str(eval(self.current_input))
            self.display.setText(result)
            self.current_input = result
        except:
            self.display.setText("Error")
            self.current_input = ""

    def clear_display(self):
        self.current_input = ""
        self.display.setText("0")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IPhoneCalculator()
    window.show()
    sys.exit(app.exec_())
