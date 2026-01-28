import sys
import hashlib
import string

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt


class PasswordGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hash-Based Password Generator")
        self.setFixedSize(400, 420)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Master password
        self.master_input = QLineEdit()
        self.master_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("Master Password"))
        layout.addWidget(self.master_input)

        # Site name
        self.site_input = QLineEdit()
        layout.addWidget(QLabel("Site / App Name"))
        layout.addWidget(self.site_input)

        # Salt
        self.salt_input = QLineEdit()
        layout.addWidget(QLabel("Salt (optional)"))
        layout.addWidget(self.salt_input)

        # Password length
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Password Length"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)

        # Character options
        self.upper_cb = QCheckBox("Uppercase")
        self.lower_cb = QCheckBox("Lowercase")
        self.digits_cb = QCheckBox("Digits")
        self.symbols_cb = QCheckBox("Symbols")

        self.upper_cb.setChecked(True)
        self.lower_cb.setChecked(True)
        self.digits_cb.setChecked(True)

        layout.addWidget(self.upper_cb)
        layout.addWidget(self.lower_cb)
        layout.addWidget(self.digits_cb)
        layout.addWidget(self.symbols_cb)

        # Generate button
        self.generate_btn = QPushButton("Generate Password")
        self.generate_btn.clicked.connect(self.generate_password)
        layout.addWidget(self.generate_btn)

        # Output
        self.output = QLineEdit()
        self.output.setReadOnly(True)
        layout.addWidget(QLabel("Generated Password"))
        layout.addWidget(self.output)

        # Copy button
        self.copy_btn = QPushButton("Copy to Clipboard")
        self.copy_btn.clicked.connect(self.copy_password)
        layout.addWidget(self.copy_btn)

        self.setLayout(layout)

    def generate_password(self):
        master = self.master_input.text()
        site = self.site_input.text()
        salt = self.salt_input.text()

        if not master or not site:
            QMessageBox.warning(self, "Error", "Master password and site name are required.")
            return

        charset = ""
        if self.upper_cb.isChecked():
            charset += string.ascii_uppercase
        if self.lower_cb.isChecked():
            charset += string.ascii_lowercase
        if self.digits_cb.isChecked():
            charset += string.digits
        if self.symbols_cb.isChecked():
            charset += "!@#$%^&*()-_=+[]{};:,.<>?"

        if not charset:
            QMessageBox.warning(self, "Error", "Select at least one character set.")
            return

        length = self.length_spin.value()

        base_string = master + site + salt
        hash_hex = hashlib.sha256(base_string.encode()).hexdigest()

        password = ""
        for i in range(length):
            index = int(hash_hex[i * 2:i * 2 + 2], 16)
            password += charset[index % len(charset)]

        self.output.setText(password)

    def copy_password(self):
        QApplication.clipboard().setText(self.output.text())
        QMessageBox.information(self, "Copied", "Password copied to clipboard!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordGenerator()
    window.show()
    sys.exit(app.exec())
