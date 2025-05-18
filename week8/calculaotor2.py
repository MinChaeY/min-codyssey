import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt

MAX_VALUE = 1e100

class Calculator:
    def __init__(self):
        self.reset()

    def reset(self):
        self.expression = ''
        self.tokens = []
        self.current_input = ''
        self.result = None

    def input_number(self, num):
        if num == '.' and '.' in self.current_input:
            return
        self.current_input += num
        self.expression += num

    def input_operator(self, op):
        if self.current_input:
            self.tokens.append(self.current_input)
            self.current_input = ''
        if self.tokens and self.tokens[-1] in '+-*/':
            self.tokens[-1] = op
            self.expression = self.expression[:-1] + op
        else:
            self.tokens.append(op)
            self.expression += op

    def toggle_sign(self):
        if self.current_input:
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.expression = ''.join(self.tokens) + self.current_input

    def percent(self):
        # 사용자 입력이 있을 경우 퍼센트 표시만 추가하고 실제 계산은 equal()에서 진행
        if self.current_input:
            self.tokens.append(self.current_input)
            self.tokens.append('%')
            self.expression += '%'
            self.current_input = ''

    def equal(self):
        if self.current_input:
            self.tokens.append(self.current_input)
        try:
            expanded_tokens = self.expand_percent_tokens(self.tokens)
            postfix = self.infix_to_postfix(expanded_tokens)
            result = self.eval_postfix(postfix)
            if isinstance(result, float) and abs(result) > MAX_VALUE:
                raise OverflowError
            self.result = str(round(result, 6)) if isinstance(result, float) else result
        except ZeroDivisionError:
            self.result = '정의되지 않음'
        except OverflowError:
            self.result = 'Overflow'
        except:
            self.result = '정의되지 않음'

        self.current_input = self.result
        self.expression = self.result
        self.tokens = []
        return self.result

    def expand_percent_tokens(self, tokens):
        # '%' 토큰을 발견하면 그 앞 숫자를 100으로 나눈 값으로 치환
        output = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '%':
                if output:
                    prev = output.pop()
                    output.append(str(float(prev) / 100))
            else:
                output.append(token)
            i += 1
        return output

    def infix_to_postfix(self, tokens):
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
        output = []
        stack = []
        for token in tokens:
            if token in '+-*/':
                while stack and precedence.get(stack[-1], 0) >= precedence[token]:
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        return output

    def eval_postfix(self, postfix):
        stack = []
        for token in postfix:
            if token not in '+-*/':
                stack.append(float(token))
            else:
                b = stack.pop()
                a = stack.pop()
                if token == '+':
                    stack.append(a + b)
                elif token == '-':
                    stack.append(a - b)
                elif token == '*':
                    stack.append(a * b)
                elif token == '/':
                    if b == 0:
                        raise ZeroDivisionError
                    stack.append(a / b)
        return stack[0]

    def get_display_text(self):
        return self.expression if self.expression else '0'


class IPhoneCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('iPhone Calculator')
        self.setStyleSheet('background-color: black;')
        self.setFixedSize(390, 650)
        self.calculator = Calculator()
        self.init_ui()

    def init_ui(self):
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.display.setStyleSheet(self.get_display_style(64))

        buttons = [
            ['AC', '+/-', '%', '÷'],
            ['7', '8', '9', '×'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['0', '.', '=']
        ]

        grid = QGridLayout()
        grid.setSpacing(10)

        for row, line in enumerate(buttons):
            col = 0
            for btn_text in line:
                button = QPushButton(btn_text)
                if btn_text == '0':
                    button.setFixedSize(170, 80)
                    grid.addWidget(button, row + 1, 0, 1, 2)
                    col += 1
                else:
                    button.setFixedSize(80, 80)
                    grid.addWidget(button, row + 1, col if btn_text != '0' else 2, 1, 1)

                if btn_text in ['AC', '+/-', '%']:
                    button.setStyleSheet(self.style_function_btn())
                elif btn_text in ['+', '-', '×', '÷', '=']:
                    button.setStyleSheet(self.style_operator_btn())
                else:
                    button.setStyleSheet(self.style_number_btn())

                if btn_text.isdigit() or btn_text == '.':
                    button.clicked.connect(lambda checked, text=btn_text: self.input_number(text))
                elif btn_text in ['+', '-', '×', '÷']:
                    button.clicked.connect(lambda checked, op=btn_text: self.input_operator(op))
                elif btn_text == '=':
                    button.clicked.connect(self.calculate_result)
                elif btn_text == 'AC':
                    button.clicked.connect(self.clear_display)
                elif btn_text == '+/-':
                    button.clicked.connect(self.toggle_sign)
                elif btn_text == '%':
                    button.clicked.connect(self.percent)

                col += 1

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.addWidget(self.display)
        layout.addLayout(grid)
        self.setLayout(layout)

    def input_number(self, num):
        self.calculator.input_number(num)
        self.update_display()

    def input_operator(self, op):
        symbol = {'×': '*', '÷': '/'}
        self.calculator.input_operator(symbol.get(op, op))
        self.update_display()

    def toggle_sign(self):
        self.calculator.toggle_sign()
        self.update_display()

    def percent(self):
        self.calculator.percent()
        self.update_display()

    def calculate_result(self):
        result = self.calculator.equal()
        self.update_display()

    def clear_display(self):
        self.calculator.reset()
        self.update_display()

    def update_display(self):
        text = self.calculator.get_display_text()
        font_size = 64
        if len(text) > 9:
            font_size = 48
        if len(text) > 15:
            font_size = 32
        self.display.setStyleSheet(self.get_display_style(font_size))
        self.display.setText(text)

    def get_display_style(self, size):
        return f'''
            color: white;
            font-size: {size}px;
            padding: 30px 10px 10px 10px;
            font-family: 'Arial';
        '''

    def style_number_btn(self):
        return '''
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
        '''

    def style_operator_btn(self):
        return '''
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
        '''

    def style_function_btn(self):
        return '''
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
        '''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = IPhoneCalculator()
    window.show()
    sys.exit(app.exec_())
