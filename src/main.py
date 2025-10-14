import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QLineEdit, QPushButton,
                            QMessageBox, QStackedWidget, QSizePolicy, QSpacerItem)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from database import Database
from admin_view import AdminView
from employee_view import EmployeeView
import qt_material

class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Spacer atas
        main_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Card login
        card = QWidget()
        card_layout = QVBoxLayout()
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(18)
        card.setLayout(card_layout)
        card.setStyleSheet("""
            background: #23272f;
            border-radius: 12px;
            padding: 28px 32px 20px 32px;
            min-width: 320px;
            max-width: 400px;
            box-shadow: 0 4px 24px 0 rgba(31,38,135,0.18);
        """)

        # Logo/ikon (opsional, bisa ganti path jika ada logo)
        logo = QLabel()
        logo.setPixmap(QPixmap().scaled(64, 64))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(logo)

        # Judul besar
        title = QLabel("Sistem Penggajian Karyawan")
        title.setStyleSheet("font-size: 19px; font-weight: bold; color: #fff; margin-bottom: 12px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Username
        username_label = QLabel("Nama Pengguna:")
        username_label.setStyleSheet("color: #fff; font-weight: bold; margin-bottom: 2px; font-size: 14px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Masukkan NIP/Admin")
        self.username_input.setStyleSheet(
            """
            padding: 8px; border-radius: 6px; font-size: 15px;
            background: #181a20; color: #fff; border: 1px solid #444;
            """
        )
        self.username_input.setMinimumHeight(36)
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Kata Sandi:")
        password_label.setStyleSheet("color: #fff; font-weight: bold; margin-bottom: 2px; font-size: 14px;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Masukkan kata sandi")
        self.password_input.setStyleSheet(
            """
            padding: 8px; border-radius: 6px; font-size: 15px;
            background: #181a20; color: #fff; border: 1px solid #444;
            """
        )
        self.password_input.setMinimumHeight(36)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        login_button.setStyleSheet("""
            padding: 10px;
            font-weight: bold;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2196f3, stop:1 #21cbf3);
            color: #fff;
            border-radius: 6px;
            font-size: 15px;
        """)
        login_button.setMinimumHeight(38)
        login_button.setMinimumWidth(0)
        card_layout.addWidget(login_button)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        # Spacer bawah
        main_layout.addSpacerItem(QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.setLayout(main_layout)
        self.setStyleSheet("background: #181a20;")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        role = self.db.verify_user(username, password)
        if role:
            self.main_window.show_main_window(role, username)
        else:
            QMessageBox.warning(self, "Error", "Nama pengguna atau kata sandi tidak valid!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Penggajian Karyawan")
        self.setGeometry(100, 100, 800, 600)
        self.db = Database()
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create admin and employee views
        self.admin_view = AdminView(main_window=self)
        self.employee_view = EmployeeView(main_window=self)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.admin_view)
        self.stacked_widget.addWidget(self.employee_view)
        
        # Add login window
        self.login_window = LoginWindow(self)
        self.stacked_widget.addWidget(self.login_window)
        
        # Show login window first
        self.stacked_widget.setCurrentWidget(self.login_window)

    def show_main_window(self, role, username):
        if role == "admin":
            self.stacked_widget.setCurrentWidget(self.admin_view)
        else:
            # For employee view, we need to set the employee info
            employee = self.db.get_employee(nip=username)
            if employee:
                self.employee_view.set_employee_info(employee[0])  # employee[0] is the ID
                self.stacked_widget.setCurrentWidget(self.employee_view)
            else:
                QMessageBox.warning(self, "Error", "Employee data not found")

    def show_login_window(self):
        self.stacked_widget.setCurrentWidget(self.login_window)
        # Optionally clear login fields
        self.login_window.username_input.clear()
        self.login_window.password_input.clear()

def main():
    app = QApplication(sys.argv)
    qt_material.apply_stylesheet(app, theme='dark_blue.xml')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 