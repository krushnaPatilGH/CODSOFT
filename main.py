import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QGridLayout, QPushButton,
    QLineEdit, QListWidget, QHBoxLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QIcon
from logic.engine import SafeCalculator


class Calculator(QMainWindow):
    FUNCTION_TOKENS = [
        "sin(", "cos(", "tan(", "log(",
        "sqrt(", "pi", "Error"
    ]

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Calculator")
        self.setFixedSize(560, 580)
        self.setWindowIcon(QIcon("calc_icon.ico"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setFocusPolicy(Qt.StrongFocus)
        self.central_widget.setFocusPolicy(Qt.StrongFocus)
        self.central_widget.setFocus()

        self.root_layout = QHBoxLayout(self.central_widget)
        self.left_layout = QVBoxLayout()
        self.root_layout.addLayout(self.left_layout, 3)

        self.left_layout.setSpacing(15)
        self.left_layout.setContentsMargins(15, 15, 15, 15)

        self.create_display()
        self.create_buttons()
        self.create_history()

        self.apply_style()
        self.engine = SafeCalculator()

    # ------------------- Animations -------------------
    def animate_button(self, button):
        original_rect = button.geometry()
        shrink_rect = QRect(
            original_rect.x() + 3,
            original_rect.y() + 3,
            original_rect.width() - 6,
            original_rect.height() - 6
        )

        animation = QPropertyAnimation(button, b"geometry")
        animation.setDuration(120)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.setStartValue(original_rect)
        animation.setKeyValueAt(0.5, shrink_rect)
        animation.setEndValue(original_rect)
        animation.start()

        # Prevent garbage collection
        button._animation = animation

    # ------------------- Display -------------------
    def create_display(self):
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(80)
        self.display.setText("0")

        font = QFont("Segoe UI", 28)
        self.display.setFont(font)
        self.display.setFocusPolicy(Qt.NoFocus)
        self.left_layout.addWidget(self.display)

    # ------------------- Buttons -------------------
    def create_buttons(self):
        self.grid = QGridLayout()
        self.grid.setSpacing(10)

        buttons = [
            # Scientific row
            ("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2), ("(", 0, 3),

            # Control row
            ("C", 1, 0), ("⌫", 1, 1), ("/", 1, 2), (")", 1, 3),

            # Numbers
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2), ("*", 2, 3),
            ("4", 3, 0), ("5", 3, 1), ("6", 3, 2), ("-", 3, 3),
            ("1", 4, 0), ("2", 4, 1), ("3", 4, 2), ("+", 4, 3),

            # Bottom row
            (".", 5, 0), ("0", 5, 1), ("√", 5, 2), ("=", 5, 3)
        ]

        for btn in buttons:
            if len(btn) == 3:
                text, row, col = btn
                rowspan, colspan = 1, 1
            else:
                text, row, col, rowspan, colspan = btn

            button = QPushButton(text)
            button.setFixedSize(75, 65)
            button.setFont(QFont("Segoe UI", 14))
            button.clicked.connect(
                lambda _, b=button, t=text: (
                    self.animate_button(b),
                    self.on_button_click(t)
                )
            )
            self.grid.addWidget(button, row, col, rowspan, colspan)

        self.left_layout.addLayout(self.grid)

    # ------------------- Input Handling -------------------
    def append_text(self, text):
        current = self.display.text()
        last = current[-1] if current else ""

        # Reset after Error
        if current == "Error":
            current = ""

        # Replace starting 0
        if current == "0" and text not in (".", ")"):
            current = ""

        # Prevent double operators
        if self.is_operator(text):
            if not current or self.is_operator(last) or last == "(":
                return

        # Prevent multiple dots in the same number
        if text == ".":
            num = ""
            for ch in reversed(current):
                if ch.isdigit() or ch == ".":
                    num += ch
                else:
                    break
            if "." in num:
                return

        # Prevent empty brackets ()
        if text == ")" and last == "(":
            return

        # Prevent unmatched closing bracket
        if text == ")" and self.bracket_balance() <= 0:
            return

        # Prevent opening bracket after number without operator
        if text == "(" and last.isdigit():
            return

        self.display.setText(current + text)

    def is_operator(self, ch):
        return ch in "+-*/"

    def bracket_balance(self):
        text = self.display.text()
        return text.count("(") - text.count(")")

    # ------------------- Keyboard Events -------------------
    def keyPressEvent(self, event):
        key = event.key()

        if Qt.Key_0 <= key <= Qt.Key_9:
            self.on_button_click(chr(key))
        elif key == Qt.Key_Plus:
            self.on_button_click("+")
        elif key == Qt.Key_Minus:
            self.on_button_click("-")
        elif key == Qt.Key_Asterisk:
            self.on_button_click("*")
        elif key == Qt.Key_Slash:
            self.on_button_click("/")
        elif key == Qt.Key_Enter or key == Qt.Key_Return:
            self.on_button_click("=")
        elif key == Qt.Key_Backspace:
            self.on_button_click("⌫")
        elif key == Qt.Key_Escape or key == Qt.Key_Delete:
            self.on_button_click("C")
        elif key == Qt.Key_Period:
            self.on_button_click(".")
        elif key == Qt.Key_ParenLeft:
            self.on_button_click("(")
        elif key == Qt.Key_ParenRight:
            self.on_button_click(")")
        else:
            super().keyPressEvent(event)

    # ------------------- Button Actions -------------------
    def on_button_click(self, text):
        if text == "C":
            self.display.setText("0")
        elif text == "⌫":
            self.smart_backspace()
        elif text in ("+", "-", "*", "/"):
            self.append_text(text)
        elif text in ("sin", "cos", "tan", "log"):
            self.append_text(f"{text}(")
        elif text == "√":
            self.append_text("sqrt(")
        elif text == "π":
            self.append_text("pi")
        elif text == "(":
            self.append_text("(")
        elif text == ")":
            self.append_text(")")
        elif text == "=":
            try:
                expression = self.display.text()
                result = self.engine.evaluate(expression)
                self.display.setText(str(result))
                self.history.addItem(f"{expression} = {result}")
            except:
                self.display.setText("Error")
        else:
            self.append_text(text)

    # ------------------- Backspace -------------------
    def smart_backspace(self):
        current = self.display.text()

        if current in ("0", "Error"):
            self.display.setText("0")
            return

        for token in self.FUNCTION_TOKENS:
            if current.endswith(token):
                new_text = current[:-len(token)]
                self.display.setText(new_text if new_text else "0")
                return

        new_text = current[:-1]
        self.display.setText(new_text if new_text else "0")

    # ------------------- History -------------------
    def create_history(self):
        self.history = QListWidget()
        self.history.setFixedWidth(170)
        self.history.itemClicked.connect(self.load_from_history)
        self.root_layout.addWidget(self.history, 1)

    def load_from_history(self, item):
        expression = item.text().split("=")[0].strip()
        self.display.setText(expression)

    # ------------------- Styling -------------------
    def apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLineEdit {
                background-color: #1e1e1e;
                color: white;
                border-radius: 10px;
                padding: 15px;
            }
            QPushButton {
                background-color: #1e1e1e;
                color: white;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #cccccc;
                border-radius: 10px;
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #2a2a2a;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
