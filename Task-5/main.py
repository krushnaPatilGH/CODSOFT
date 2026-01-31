import sys
import json
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox
)
from PySide6.QtCore import Qt


DATA_FILE = "contacts.json"


class ContactBook(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Book")
        self.setFixedSize(600, 420)
        self.contacts = []
        self.load_contacts()
        self.init_ui()
        self.load_table()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input fields
        form = QHBoxLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()

        self.name_input.setPlaceholderText("Name")
        self.phone_input.setPlaceholderText("Phone")
        self.email_input.setPlaceholderText("Email")

        form.addWidget(self.name_input)
        form.addWidget(self.phone_input)
        form.addWidget(self.email_input)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.update_btn = QPushButton("Update")
        self.delete_btn = QPushButton("Delete")

        self.add_btn.clicked.connect(self.add_contact)
        self.update_btn.clicked.connect(self.update_contact)
        self.delete_btn.clicked.connect(self.delete_contact)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        layout.addLayout(btn_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Phone", "Email"])
        self.table.cellClicked.connect(self.select_contact)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def load_contacts(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.contacts = json.load(f)

    def save_contacts(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.contacts, f, indent=4)

    def load_table(self):
        self.table.setRowCount(len(self.contacts))
        for row, contact in enumerate(self.contacts):
            self.table.setItem(row, 0, QTableWidgetItem(contact["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(contact["phone"]))
            self.table.setItem(row, 2, QTableWidgetItem(contact["email"]))

    def add_contact(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Error", "Name and Phone are required.")
            return

        self.contacts.append({
            "name": name,
            "phone": phone,
            "email": email
        })

        self.save_contacts()
        self.load_table()
        self.clear_inputs()

    def select_contact(self, row, _):
        contact = self.contacts[row]
        self.name_input.setText(contact["name"])
        self.phone_input.setText(contact["phone"])
        self.email_input.setText(contact["email"])
        self.selected_row = row

    def update_contact(self):
        if not hasattr(self, "selected_row"):
            QMessageBox.warning(self, "Error", "Select a contact first.")
            return

        self.contacts[self.selected_row] = {
            "name": self.name_input.text(),
            "phone": self.phone_input.text(),
            "email": self.email_input.text()
        }

        self.save_contacts()
        self.load_table()
        self.clear_inputs()

    def delete_contact(self):
        if not hasattr(self, "selected_row"):
            QMessageBox.warning(self, "Error", "Select a contact first.")
            return

        self.contacts.pop(self.selected_row)
        self.save_contacts()
        self.load_table()
        self.clear_inputs()

    def clear_inputs(self):
        self.name_input.clear()
        self.phone_input.clear()
        self.email_input.clear()
        if hasattr(self, "selected_row"):
            del self.selected_row


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ContactBook()
    window.show()
    sys.exit(app.exec())
