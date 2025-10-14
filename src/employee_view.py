from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QDateEdit, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from database import Database
import os
from datetime import datetime

class EmployeeView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window # Store reference to main_window
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with Logout Button
        header_layout = QHBoxLayout()
        self.header_label = QLabel("Selamat Datang, Karyawan!")
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)

        header_layout.addWidget(self.header_label)
        header_layout.addStretch(1)
        header_layout.addWidget(logout_button)
        layout.addLayout(header_layout)

        # Profile Section
        profile_layout = QVBoxLayout()
        self.profile_label = QLabel("Profil Karyawan")
        self.profile_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        profile_layout.addWidget(self.profile_label)
        
        # Profile Details
        self.name_label = QLabel()
        self.position_label = QLabel()
        self.department_label = QLabel()
        self.join_date_label = QLabel()
        
        profile_layout.addWidget(self.name_label)
        profile_layout.addWidget(self.position_label)
        profile_layout.addWidget(self.department_label)
        profile_layout.addWidget(self.join_date_label)
        
        layout.addLayout(profile_layout)
        
        # Salary Information
        salary_layout = QVBoxLayout()
        salary_header = QLabel("Informasi Gaji")
        salary_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        salary_layout.addWidget(salary_header)
        
        # Month and Year Selection
        date_layout = QHBoxLayout()
        self.month_combo = QComboBox()
        self.month_combo.addItems([str(i) for i in range(1, 13)])
        self.year_combo = QComboBox()
        self.year_combo.addItems([str(i) for i in range(2020, datetime.now().year + 2)])
        # Set default bulan dan tahun ke hari ini
        today = datetime.now()
        self.month_combo.setCurrentText(str(today.month))
        self.year_combo.setCurrentText(str(today.year))
        
        date_layout.addWidget(QLabel("Bulan:"))
        date_layout.addWidget(self.month_combo)
        date_layout.addWidget(QLabel("Tahun:"))
        date_layout.addWidget(self.year_combo)
        
        view_button = QPushButton("Lihat Gaji")
        view_button.clicked.connect(self.view_salary)
        date_layout.addWidget(view_button)
        
        salary_layout.addLayout(date_layout)
        
        # Salary Components Table
        self.salary_table = QTableWidget()
        self.salary_table.setColumnCount(3)
        self.salary_table.setHorizontalHeaderLabels([
            "Tipe Komponen", "Jumlah", "Tanggal"
        ])
        salary_layout.addWidget(self.salary_table)
        
        # Total Salary
        self.total_salary_label = QLabel()
        self.total_salary_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        salary_layout.addWidget(self.total_salary_label)
        
        layout.addLayout(salary_layout)
        
        # Attendance Section
        attendance_layout = QVBoxLayout()
        attendance_header = QLabel("Catatan Absensi")
        attendance_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        attendance_layout.addWidget(attendance_header)
        
        # Date Range Selection
        date_range_layout = QHBoxLayout()
        self.start_date = QDateEdit()
        today = QDate.currentDate()
        # Set start_date ke tanggal 1 bulan & tahun sekarang
        self.start_date.setDate(QDate(today.year(), today.month(), 1))
        self.end_date = QDateEdit()
        # Set end_date ke tanggal terakhir bulan & tahun sekarang
        last_day = QDate(today.year(), today.month(), 1).daysInMonth()
        self.end_date.setDate(QDate(today.year(), today.month(), last_day))
        
        date_range_layout.addWidget(QLabel("Tanggal Mulai:"))
        date_range_layout.addWidget(self.start_date)
        date_range_layout.addWidget(QLabel("Tanggal Akhir:"))
        date_range_layout.addWidget(self.end_date)
        
        view_attendance_button = QPushButton("Lihat Absensi")
        view_attendance_button.clicked.connect(self.view_attendance)
        date_range_layout.addWidget(view_attendance_button)
        
        attendance_layout.addLayout(date_range_layout)
        
        # Attendance Table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels([
            "Tanggal", "Check In", "Check Out", "Status"
        ])
        attendance_layout.addWidget(self.attendance_table)
        
        layout.addLayout(attendance_layout)
        
        # Processed Payslips Section
        payslips_layout = QVBoxLayout()
        payslips_header = QLabel("Riwayat Slip Gaji")
        payslips_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        payslips_layout.addWidget(payslips_header)

        self.employee_payslip_table = QTableWidget()
        self.employee_payslip_table.setColumnCount(4)
        self.employee_payslip_table.setHorizontalHeaderLabels([
            "Tipe Komponen", "Jumlah", "Bulan", "Tahun"
        ])
        payslips_layout.addWidget(self.employee_payslip_table)

        layout.addLayout(payslips_layout)
        
        self.setLayout(layout)

    def set_employee_info(self, employee_id):
        employee = self.db.get_employee(employee_id=employee_id)
        if employee:
            self.employee_id = employee[0]  # Store employee ID
            self.profile_label.setText(f"Profil Karyawan: {employee[2]} ({employee[1]})")
            self.name_label.setText(f"Nama: {employee[2]}")
            self.position_label.setText(f"Jabatan: {employee[3]}")
            self.department_label.setText(f"Departemen: {employee[4]}")
            self.join_date_label.setText(f"Tanggal Bergabung: {employee[6]}")
            self.header_label.setText(f"Selamat Datang, {employee[2]}!") # Update header
            # Load initial salary and attendance data for the employee
            self.view_salary()
            self.view_attendance()
            self.load_employee_payslips()

    def logout(self):
        if self.main_window:
            self.main_window.show_login_window()

    def view_salary(self):
        self.salary_table.setRowCount(0)
        employee_id = getattr(self, 'employee_id', None)
        if not employee_id:
            QMessageBox.warning(self, "Error", "Mohon pilih karyawan terlebih dahulu.")
            return

        month = int(self.month_combo.currentText())
        year = int(self.year_combo.currentText())
        
        salary_components = self.db.get_salary_components(employee_id, month, year)
        total_salary = 0.0
        for row_num, component in enumerate(salary_components):
            self.salary_table.insertRow(row_num)
            self.salary_table.setItem(row_num, 0, QTableWidgetItem(str(component[2])))
            self.salary_table.setItem(row_num, 1, QTableWidgetItem(f"{component[3]:,.2f}"))
            self.salary_table.setItem(row_num, 2, QTableWidgetItem(f"{component[4]}/{component[5]}")) # Month/Year

            # Perbaikan: Potongan, Pajak, Asuransi harus mengurangi total gaji
            if component[2] in ["Potongan", "Pajak", "Asuransi"]:
                total_salary -= component[3]
            else:
                total_salary += component[3]
        self.total_salary_label.setText(f"Total Gaji: Rp {total_salary:,.2f}")

    def view_attendance(self):
        self.attendance_table.setRowCount(0)
        employee_id = getattr(self, 'employee_id', None)
        if not employee_id:
            QMessageBox.warning(self, "Error", "Mohon pilih karyawan terlebih dahulu.")
            return

        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")
        
        attendance_records = self.db.get_attendance(employee_id, start_date, end_date)
        for row_num, record in enumerate(attendance_records):
            self.attendance_table.insertRow(row_num)
            self.attendance_table.setItem(row_num, 0, QTableWidgetItem(str(record[2])))
            self.attendance_table.setItem(row_num, 1, QTableWidgetItem(str(record[3] or "-")))
            self.attendance_table.setItem(row_num, 2, QTableWidgetItem(str(record[4] or "-")))
            self.attendance_table.setItem(row_num, 3, QTableWidgetItem(str(record[5])))

    def calculate_total_salary(self, components):
        total = sum(component[3] for component in components)  # Assuming amount is at index 3
        self.total_salary_label.setText(f"Total Gaji: Rp {total:,.2f}")

    def load_employee_payslips(self):
        self.employee_payslip_table.setRowCount(0)
        employee_id = getattr(self, 'employee_id', None)
        if not employee_id:
            return
        # Ambil komponen gaji yang termasuk tunjangan, lembur, bonus, potongan, pajak, asuransi
        allowed_types = ["Tunjangan", "Lembur", "Bonus", "Potongan", "Pajak", "Asuransi"]
        components = self.db.cursor.execute(
            "SELECT component_type, amount, month, year FROM salary_components WHERE employee_id = ? AND component_type IN (?, ?, ?, ?, ?, ?)",
            (employee_id, *allowed_types)
        ).fetchall()
        self.employee_payslip_table.setColumnCount(4)
        self.employee_payslip_table.setHorizontalHeaderLabels([
            "Tipe Komponen", "Jumlah", "Bulan", "Tahun"
        ])
        for row_num, comp in enumerate(components):
            self.employee_payslip_table.insertRow(row_num)
            self.employee_payslip_table.setItem(row_num, 0, QTableWidgetItem(str(comp[0])))
            self.employee_payslip_table.setItem(row_num, 1, QTableWidgetItem(f"{comp[1]:,.2f}"))
            self.employee_payslip_table.setItem(row_num, 2, QTableWidgetItem(str(comp[2])))
            self.employee_payslip_table.setItem(row_num, 3, QTableWidgetItem(str(comp[3])))

    def open_pdf(self, filepath):
        try:
            os.startfile(filepath)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal membuka PDF: {e}") 