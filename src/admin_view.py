from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QComboBox, QLineEdit, QDateEdit, QMessageBox,
                            QTabWidget, QFormLayout, QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from database import Database
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import os

class AdminView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window # Store reference to main_window
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header with Logout Button
        header_layout = QHBoxLayout()
        header_label = QLabel("Selamat Datang, Admin!")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)

        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        header_layout.addWidget(logout_button)
        layout.addLayout(header_layout)

        # Create tab widget
        tabs = QTabWidget()
        
        # Employee Management Tab
        employee_tab = QWidget()
        employee_layout = QVBoxLayout()
        
        # Add Employee Form
        form_layout = QFormLayout()
        self.nip_input = QLineEdit()
        self.name_input = QLineEdit()
        self.position_input = QLineEdit()
        self.department_input = QLineEdit()
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText("Masukkan nilai numerik untuk gaji")
        self.join_date_input = QDateEdit()
        self.join_date_input.setDate(QDate.currentDate())
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Tidak Aktif"])
        
        form_layout.addRow("NIP:", self.nip_input)
        form_layout.addRow("Nama:", self.name_input)
        form_layout.addRow("Jabatan:", self.position_input)
        form_layout.addRow("Departemen:", self.department_input)
        form_layout.addRow("Gaji Pokok:", self.salary_input)
        form_layout.addRow("Tanggal Bergabung:", self.join_date_input)
        form_layout.addRow("Status:", self.status_input)
        
        self.add_button = QPushButton("Tambah Karyawan") # Made it a self attribute
        self.add_button.clicked.connect(self.add_employee)
        form_layout.addRow(self.add_button)
        
        employee_layout.addLayout(form_layout)
        
        # Employee List Table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(8)
        self.employee_table.setHorizontalHeaderLabels([
            "ID", "NIP", "Nama", "Jabatan", "Departemen",
            "Gaji Pokok", "Tanggal Bergabung", "Status"
        ])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.employee_table.horizontalHeader().setMinimumSectionSize(160)
        employee_layout.addWidget(self.employee_table)
        
        # Edit/Delete Buttons
        employee_buttons_layout = QHBoxLayout()
        self.edit_employee_button = QPushButton("Edit Karyawan")
        self.edit_employee_button.clicked.connect(self.edit_employee)
        self.delete_employee_button = QPushButton("Hapus Karyawan")
        self.delete_employee_button.clicked.connect(self.delete_employee)
        
        employee_buttons_layout.addWidget(self.edit_employee_button)
        employee_buttons_layout.addWidget(self.delete_employee_button)
        employee_layout.addLayout(employee_buttons_layout)

        # Export to Excel Button for Employees
        export_employee_button = QPushButton("Ekspor Karyawan ke Excel")
        export_employee_button.clicked.connect(self.export_employees_to_excel)
        employee_layout.addWidget(export_employee_button)
        
        employee_tab.setLayout(employee_layout)
        
        # Salary Management Tab
        salary_tab = QWidget()
        salary_layout = QVBoxLayout()
        
        # Salary Component Form
        salary_form = QFormLayout()
        self.employee_combo = QComboBox()
        self.component_type = QComboBox()
        self.component_type.addItems([
            "Gaji Pokok", "Tunjangan", "Lembur", "Bonus",
            "Potongan", "Pajak", "Asuransi"
        ])
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Masukkan nilai numerik untuk jumlah")
        self.month_input = QComboBox()
        self.month_input.addItems([str(i) for i in range(1, 13)])
        self.year_input = QComboBox()
        self.year_input.addItems([str(i) for i in range(2020, datetime.now().year + 1)])
        # Set default bulan dan tahun ke hari ini
        today = datetime.now()
        self.month_input.setCurrentText(str(today.month))
        self.year_input.setCurrentText(str(today.year))
        
        salary_form.addRow("Karyawan:", self.employee_combo)
        salary_form.addRow("Tipe Komponen:", self.component_type)
        salary_form.addRow("Jumlah:", self.amount_input)
        salary_form.addRow("Bulan:", self.month_input)
        salary_form.addRow("Tahun:", self.year_input)
        
        self.add_component_button = QPushButton("Tambah Komponen") # Made it a self attribute
        self.add_component_button.clicked.connect(self.add_salary_component)
        salary_form.addRow(self.add_component_button)
        
        salary_layout.addLayout(salary_form)
        
        # Salary Components Table
        self.salary_table = QTableWidget()
        self.salary_table.setColumnCount(6)
        self.salary_table.setHorizontalHeaderLabels([
            "ID", "Karyawan", "Tipe Komponen", "Jumlah", "Bulan", "Tahun"
        ])
        self.salary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.salary_table.horizontalHeader().setMinimumSectionSize(160)
        salary_layout.addWidget(self.salary_table)
        
        # Edit/Delete Buttons for Salary Components
        salary_buttons_layout = QHBoxLayout()
        self.edit_component_button = QPushButton("Edit Komponen")
        self.edit_component_button.clicked.connect(self.edit_salary_component)
        self.delete_component_button = QPushButton("Hapus Komponen")
        self.delete_component_button.clicked.connect(self.delete_salary_component)

        salary_buttons_layout.addWidget(self.edit_component_button)
        salary_buttons_layout.addWidget(self.delete_component_button)
        salary_layout.addLayout(salary_buttons_layout)

        # Export to Excel Button for Salary Components
        export_salary_button = QPushButton("Ekspor Komponen Gaji ke Excel")
        export_salary_button.clicked.connect(self.export_salary_components_to_excel)
        salary_layout.addWidget(export_salary_button)
        
        salary_tab.setLayout(salary_layout)

        # Payroll Processing Tab
        payroll_tab = QWidget()
        payroll_layout = QVBoxLayout()

        payroll_header = QLabel("Proses Penggajian")
        payroll_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        payroll_layout.addWidget(payroll_header)

        payroll_filter_layout = QHBoxLayout()
        payroll_filter_layout.addWidget(QLabel("Bulan Gaji:"))
        self.payroll_month_combo = QComboBox()
        self.payroll_month_combo.addItems([str(i) for i in range(1, 13)])
        payroll_filter_layout.addWidget(self.payroll_month_combo)

        payroll_filter_layout.addWidget(QLabel("Tahun Gaji:"))
        self.payroll_year_combo = QComboBox()
        self.payroll_year_combo.addItems([str(i) for i in range(2020, datetime.now().year + 1)])
        payroll_filter_layout.addWidget(self.payroll_year_combo)

        # Set default bulan dan tahun ke hari ini
        today = datetime.now()
        self.payroll_month_combo.setCurrentText(str(today.month))
        self.payroll_year_combo.setCurrentText(str(today.year))

        process_payroll_button = QPushButton("Proses Gaji")
        process_payroll_button.clicked.connect(self.process_payroll)
        payroll_filter_layout.addWidget(process_payroll_button)

        payroll_layout.addLayout(payroll_filter_layout)

        # Processed Payslips Table
        self.payslip_table = QTableWidget()
        self.payslip_table.setColumnCount(5) # Employee, Month, Year, Net Salary, Action (View PDF)
        self.payslip_table.setHorizontalHeaderLabels([
            "Nama Karyawan", "Bulan", "Tahun", "Gaji Bersih", "Aksi"
        ])
        self.payslip_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.payslip_table.horizontalHeader().setMinimumSectionSize(160)
        payroll_layout.addWidget(self.payslip_table)

        payroll_tab.setLayout(payroll_layout)
        
        # Laporan Tab
        report_tab = QWidget()
        report_layout = QVBoxLayout()

        report_header = QLabel("Laporan Rekapitulasi Gaji")
        report_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        report_layout.addWidget(report_header)

        # Filters for reports (Month, Year)
        report_filter_layout = QHBoxLayout()
        report_filter_layout.addWidget(QLabel("Bulan:"))
        self.report_month_combo = QComboBox()
        self.report_month_combo.addItems([str(i) for i in range(1, 13)])
        report_filter_layout.addWidget(self.report_month_combo)

        report_filter_layout.addWidget(QLabel("Tahun:"))
        self.report_year_combo = QComboBox()
        self.report_year_combo.addItems([str(i) for i in range(2020, datetime.now().year + 1)])
        report_filter_layout.addWidget(self.report_year_combo)

        # Set default bulan dan tahun ke hari ini
        self.report_month_combo.setCurrentText(str(today.month))
        self.report_year_combo.setCurrentText(str(today.year))

        generate_report_button = QPushButton("Buat Laporan")
        generate_report_button.clicked.connect(self.generate_salary_report)
        report_filter_layout.addWidget(generate_report_button)

        report_layout.addLayout(report_filter_layout)

        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(4) # Example: Employee, Basic Salary, Allowances, Total
        self.report_table.setHorizontalHeaderLabels([
            "Nama Karyawan", "Gaji Pokok", "Total Tunjangan/Bonus", "Total Gaji Bersih"
        ])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.report_table.horizontalHeader().setMinimumSectionSize(260)
        report_layout.addWidget(self.report_table)

        # Export Report to PDF Button
        export_report_pdf_button = QPushButton("Ekspor Laporan Gaji ke PDF")
        export_report_pdf_button.clicked.connect(self.export_salary_report_to_pdf)
        report_layout.addWidget(export_report_pdf_button)

        report_tab.setLayout(report_layout)

        # Attendance Management Tab
        attendance_admin_tab = QWidget()
        attendance_admin_layout = QVBoxLayout()

        attendance_admin_header = QLabel("Manajemen Absensi")
        attendance_admin_header.setStyleSheet("font-size: 16px; font-weight: bold;")
        attendance_admin_layout.addWidget(attendance_admin_header)

        # Attendance Form (QFormLayout)
        attendance_form = QFormLayout()
        self.attendance_employee_combo = QComboBox()
        self.attendance_date_input = QDateEdit()
        self.attendance_date_input.setDate(QDate.currentDate())
        
        self.check_in_button = QPushButton("Jam Masuk (Simpan Absensi)")
        self.check_in_button.clicked.connect(self.record_check_in)
        self.check_out_button = QPushButton("Jam Keluar (Update Absensi)")
        self.check_out_button.clicked.connect(self.record_check_out)
        
        self.attendance_status_combo = QComboBox()
        self.attendance_status_combo.addItems(["Hadir", "Sakit", "Izin", "Cuti", "Alpha"])

        attendance_form.addRow("Karyawan:", self.attendance_employee_combo)
        attendance_form.addRow("Tanggal:", self.attendance_date_input)
        attendance_form.addRow("Status (untuk Jam Masuk):", self.attendance_status_combo)
        attendance_form.addRow(self.check_in_button)
        attendance_form.addRow(self.check_out_button)

        attendance_admin_layout.addLayout(attendance_form) # Directly add the form layout

        # Attendance List Table
        self.admin_attendance_table = QTableWidget()
        self.admin_attendance_table.setColumnCount(6) # ID, Employee, Date, Check In, Check Out, Status
        self.admin_attendance_table.setHorizontalHeaderLabels([
            "ID", "Karyawan", "Tanggal", "Jam Masuk", "Jam Keluar", "Status"
        ])
        self.admin_attendance_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.admin_attendance_table.horizontalHeader().setMinimumSectionSize(160)
        attendance_admin_layout.addWidget(self.admin_attendance_table)

        attendance_admin_tab.setLayout(attendance_admin_layout)

        tabs.addTab(employee_tab, "Manajemen Karyawan")
        tabs.addTab(salary_tab, "Manajemen Gaji")
        tabs.addTab(payroll_tab, "Penggajian")
        tabs.addTab(report_tab, "Laporan")
        tabs.addTab(attendance_admin_tab, "Manajemen Absensi")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        # Load initial data
        self.load_employees()
        self.load_salary_components()
        self.load_processed_payslips()
        self.load_admin_attendance()
        self.load_attendance_employee_combo()

    def logout(self):
        if self.main_window:
            self.main_window.show_login_window()

    def add_employee(self):
        try:
            nip = self.nip_input.text()
            name = self.name_input.text()
            position = self.position_input.text()
            department = self.department_input.text()
            
            try:
                basic_salary = float(self.salary_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Gaji Pokok harus berupa angka.")
                return

            join_date = self.join_date_input.date().toString("yyyy-MM-dd")
            status = self.status_input.currentText()
            
            if not (nip and name and position and department and join_date and status):
                QMessageBox.warning(self, "Error", "Semua kolom harus diisi.")
                return

            if self.db.add_employee(nip, name, position, department, basic_salary, join_date, status):
                # Also add the employee as a user with a default password
                if self.db.add_user(nip, "123456", "employee"):
                    QMessageBox.information(self, "Berhasil", "Karyawan dan akun login berhasil ditambahkan!")
                    self.load_employees()
                    self.load_attendance_employee_combo()
                    self.clear_employee_form()
                else:
                    # If user creation fails (e.g., NIP already used as username), remove employee
                    self.db.delete_employee(self.db.get_employee(nip=nip)[0]) # Assuming get_employee by NIP returns (id, ...)
                    QMessageBox.warning(self, "Error", "Gagal menambahkan akun login karyawan. NIP mungkin sudah digunakan sebagai username.")
            else:
                QMessageBox.warning(self, "Error", "Gagal menambahkan karyawan. NIP mungkin sudah ada.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def edit_employee(self):
        selected_rows = self.employee_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Pilih karyawan yang ingin diedit.")
            return
        
        row = selected_rows[0].row()
        employee_id = int(self.employee_table.item(row, 0).text())
        employee = self.db.get_employee(employee_id=employee_id)
        
        if employee:
            self.nip_input.setText(employee[1])
            self.name_input.setText(employee[2])
            self.position_input.setText(employee[3])
            self.department_input.setText(employee[4])
            self.salary_input.setText(str(employee[5]).replace(",", ""))
            self.join_date_input.setDate(QDate.fromString(employee[6], "yyyy-MM-dd"))
            self.status_input.setCurrentText(employee[7])
            self.current_employee_id = employee_id
            # Store the current add_button text to revert later
            self._original_add_button_text = self.add_button.text()
            self.add_button.setText("Update Karyawan") 
            self.add_button.disconnect() 
            self.add_button.clicked.connect(self.update_employee_data)
            print(f"[DEBUG] Gaji Pokok saat dimuat ke form: {self.salary_input.text()}")

    def update_employee_data(self):
        try:
            employee_id = getattr(self, 'current_employee_id', None)
            if not employee_id:
                QMessageBox.warning(self, "Error", "Tidak ada karyawan yang dipilih untuk diupdate.")
                return

            nip = self.nip_input.text()
            name = self.name_input.text()
            position = self.position_input.text()
            department = self.department_input.text()
            
            try:
                basic_salary = float(self.salary_input.text().replace(",", ""))
                print(f"[DEBUG] Gaji Pokok dari input field (setelah bersih): {basic_salary}")
            except ValueError:
                QMessageBox.warning(self, "Error", "Gaji Pokok harus berupa angka.")
                return

            join_date = self.join_date_input.date().toString("yyyy-MM-dd")
            status = self.status_input.currentText()
            
            if not (nip and name and position and department and join_date and status):
                QMessageBox.warning(self, "Error", "Semua kolom harus diisi.")
                return

            if self.db.update_employee(employee_id, nip, name, position, department, basic_salary, join_date, status):
                QMessageBox.information(self, "Berhasil", "Data karyawan berhasil diperbarui")
                self.load_employees()
                self.load_attendance_employee_combo()
                self.clear_employee_form()
                # Revert button text and connection
                self.add_button.setText(self._original_add_button_text) 
                self.add_button.disconnect() 
                self.add_button.clicked.connect(self.add_employee) 
                del self.current_employee_id
                del self._original_add_button_text
            else:
                QMessageBox.warning(self, "Error", "Gagal memperbarui data karyawan. NIP mungkin sudah ada atau terjadi kesalahan lain.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def delete_employee(self):
        selected_rows = self.employee_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Pilih karyawan yang ingin dihapus.")
            return
        
        reply = QMessageBox.question(self, 'Konfirmasi Hapus', 
                                     "Anda yakin ingin menghapus karyawan ini?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            employee_id = int(self.employee_table.item(row, 0).text())
            
            if self.db.delete_employee(employee_id):
                QMessageBox.information(self, "Berhasil", "Karyawan berhasil dihapus")
                self.load_employees()
                self.load_attendance_employee_combo()
                self.clear_employee_form()
            else:
                QMessageBox.warning(self, "Error", "Gagal menghapus karyawan.")

    def add_salary_component(self):
        try:
            employee_id = self.employee_combo.currentData()
            component_type = self.component_type.currentText()
            
            try:
                amount = float(self.amount_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Jumlah harus berupa angka.")
                return

            month = int(self.month_input.currentText())
            year = int(self.year_input.currentText())
            
            if not (employee_id and component_type and amount and month and year):
                QMessageBox.warning(self, "Error", "Semua kolom komponen gaji harus diisi.")
                return

            # Disconnect update_salary_component_data if connected
            try:
                self.add_component_button.clicked.disconnect(self.update_salary_component_data)
            except TypeError: # If it's not connected, it will raise TypeError
                pass
            
            self.db.add_salary_component(employee_id, component_type, amount, month, year)
            QMessageBox.information(self, "Berhasil", "Komponen gaji berhasil ditambahkan")
            self.load_salary_components()
            self.clear_salary_form()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def edit_salary_component(self):
        selected_rows = self.salary_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Pilih komponen gaji yang ingin diedit.")
            return

        row = selected_rows[0].row()
        component_id = int(self.salary_table.item(row, 0).text())
        # We need to get the full component data including employee_id
        # The current get_salary_components method only fetches by employee_id, month, year.
        # We need a method to get a single component by its ID.
        # For now, let's just get the visible data and assume it's enough to populate.
        # Ideally, we should add a get_salary_component_by_id to database.py

        # Find the employee in the combo box by name
        employee_name = self.salary_table.item(row, 1).text()
        index = self.employee_combo.findText(employee_name, Qt.MatchFlag.MatchContains)
        if index != -1:
            self.employee_combo.setCurrentIndex(index)

        self.component_type.setCurrentText(self.salary_table.item(row, 2).text())
        self.amount_input.setText(self.salary_table.item(row, 3).text().replace(",", "")) # Remove comma for float conversion
        self.month_input.setCurrentText(self.salary_table.item(row, 4).text())
        self.year_input.setCurrentText(self.salary_table.item(row, 5).text())

        self.current_component_id = component_id
        self._original_add_component_button_text = self.add_component_button.text()
        self.add_component_button.setText("Update Komponen")
        self.add_component_button.disconnect() 
        self.add_component_button.clicked.connect(self.update_salary_component_data)

    def update_salary_component_data(self):
        try:
            component_id = getattr(self, 'current_component_id', None)
            if not component_id:
                QMessageBox.warning(self, "Error", "Tidak ada komponen gaji yang dipilih untuk diupdate.")
                return
            
            employee_id = self.employee_combo.currentData()
            component_type = self.component_type.currentText()
            
            try:
                amount = float(self.amount_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "Jumlah harus berupa angka.")
                return

            month = int(self.month_input.currentText())
            year = int(self.year_input.currentText())

            if not (employee_id and component_type and amount and month and year):
                QMessageBox.warning(self, "Error", "Semua kolom komponen gaji harus diisi.")
                return

            if self.db.update_salary_component(component_id, employee_id, component_type, amount, month, year):
                QMessageBox.information(self, "Berhasil", "Komponen gaji berhasil diperbarui")
                self.load_salary_components()
                self.clear_salary_form()
                self.add_component_button.setText(self._original_add_component_button_text)
                self.add_component_button.disconnect()
                self.add_component_button.clicked.connect(self.add_salary_component)
                del self.current_component_id
                del self._original_add_component_button_text
            else:
                QMessageBox.warning(self, "Error", "Gagal memperbarui komponen gaji.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def delete_salary_component(self):
        selected_rows = self.salary_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Error", "Pilih komponen gaji yang ingin dihapus.")
            return
        
        reply = QMessageBox.question(self, 'Konfirmasi Hapus', 
                                     "Anda yakin ingin menghapus komponen gaji ini?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected_rows[0].row()
            component_id = int(self.salary_table.item(row, 0).text())
            
            if self.db.delete_salary_component(component_id):
                QMessageBox.information(self, "Berhasil", "Komponen gaji berhasil dihapus")
                self.load_salary_components()
                self.clear_salary_form()
            else:
                QMessageBox.warning(self, "Error", "Gagal menghapus komponen gaji.")

    def load_employees(self):
        self.employee_table.setRowCount(0)
        employees = self.db.cursor.execute("SELECT * FROM employees").fetchall()
        self.employee_combo.clear()
        self.attendance_employee_combo.clear()
        for row_num, employee in enumerate(employees):
            self.employee_table.insertRow(row_num)
            for col_num, data in enumerate(employee):
                self.employee_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            self.employee_combo.addItem(f"{employee[2]} ({employee[1]})", employee[0]) # Name (NIP), ID
            self.attendance_employee_combo.addItem(f"{employee[2]} ({employee[1]})", employee[0])

    def load_salary_components(self):
        self.salary_table.setRowCount(0)
        salary_components = self.db.cursor.execute("SELECT sc.id, e.name, sc.component_type, sc.amount, sc.month, sc.year FROM salary_components sc JOIN employees e ON sc.employee_id = e.id").fetchall()
        for row_num, component in enumerate(salary_components):
            self.salary_table.insertRow(row_num)
            for col_num, data in enumerate(component):
                self.salary_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def clear_employee_form(self):
        self.nip_input.clear()
        self.name_input.clear()
        self.position_input.clear()
        self.department_input.clear()
        self.salary_input.clear()
        self.join_date_input.setDate(QDate.currentDate())
        self.status_input.setCurrentIndex(0)

    def clear_salary_form(self):
        self.amount_input.clear()
        self.component_type.setCurrentIndex(0)
        self.month_input.setCurrentIndex(0)
        self.year_input.setCurrentIndex(0)

    def export_employees_to_excel(self):
        try:
            filepath, _ = QFileDialog.getSaveFileName(self, "Ekspor Data Karyawan", "karyawan_data.xlsx", "Excel Files (*.xlsx)")
            if filepath:
                employees = self.db.get_all_employees()
                # Define column names based on the SELECT query in get_all_employees
                columns = ["ID", "NIP", "Nama", "Jabatan", "Departemen", "Gaji Pokok", "Tanggal Bergabung", "Status"]
                df = pd.DataFrame(employees, columns=columns)
                df.to_excel(filepath, index=False)
                QMessageBox.information(self, "Berhasil", "Data karyawan berhasil diekspor ke Excel!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengekspor data karyawan: {e}")

    def export_salary_components_to_excel(self):
        try:
            filepath, _ = QFileDialog.getSaveFileName(self, "Ekspor Data Komponen Gaji", "komponen_gaji_data.xlsx", "Excel Files (*.xlsx)")
            if filepath:
                salary_components = self.db.get_all_salary_components()
                # Define column names based on the SELECT query in get_all_salary_components
                columns = ["ID Komponen", "Nama Karyawan", "Tipe Komponen", "Jumlah", "Bulan", "Tahun"]
                df = pd.DataFrame(salary_components, columns=columns)
                df.to_excel(filepath, index=False)
                QMessageBox.information(self, "Berhasil", "Data komponen gaji berhasil diekspor ke Excel!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengekspor data komponen gaji: {e}")

    def generate_salary_report(self):
        self.report_table.setRowCount(0)
        month = int(self.report_month_combo.currentText())
        year = int(self.report_year_combo.currentText())

        # Fetch all employees
        employees = self.db.get_all_employees()
        
        # Prepare data for the report table
        report_data = []
        for employee_id, _, name, _, _, basic_salary, _, _ in employees:
            components = self.db.get_salary_components(employee_id, month, year)
            
            total_allowances_bonuses = 0.0
            total_deductions_taxes = 0.0
            
            for comp_id, emp_id, comp_type, amount, comp_month, comp_year in components:
                if comp_type in ["Tunjangan", "Lembur", "Bonus"]:
                    total_allowances_bonuses += amount
                elif comp_type in ["Potongan", "Pajak", "Asuransi"]:
                    total_deductions_taxes += amount
            
            total_gross_salary = basic_salary + total_allowances_bonuses
            total_net_salary = total_gross_salary - total_deductions_taxes

            report_data.append([
                name,
                f"{basic_salary:,.2f}",
                f"{total_allowances_bonuses:,.2f}",
                f"{total_net_salary:,.2f}"
            ])

        for row_num, row_data in enumerate(report_data):
            self.report_table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.report_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def export_salary_report_to_pdf(self):
        try:
            filepath, _ = QFileDialog.getSaveFileName(self, "Ekspor Laporan Gaji ke PDF", "laporan_gaji.pdf", "PDF Files (*.pdf)")
            if filepath:
                month = int(self.report_month_combo.currentText())
                year = int(self.report_year_combo.currentText())
                employees = self.db.get_all_employees()
                report_data = []
                for employee_id, _, name, _, _, basic_salary, _, _ in employees:
                    components = self.db.get_salary_components(employee_id, month, year)
                    total_allowances_bonuses = 0.0
                    total_deductions_taxes = 0.0
                    for comp_id, emp_id, comp_type, amount, comp_month, comp_year in components:
                        if comp_type in ["Tunjangan", "Bonus"]:
                            total_allowances_bonuses += amount
                        elif comp_type in ["Potongan", "Pajak", "Asuransi"]:
                            total_deductions_taxes += amount
                    total_gross_salary = basic_salary + total_allowances_bonuses
                    total_net_salary = total_gross_salary - total_deductions_taxes
                    report_data.append([
                        name,
                        f"{basic_salary:,.2f}",
                        f"{total_allowances_bonuses:,.2f}",
                        f"{total_net_salary:,.2f}"
                    ])
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.units import inch
                doc = SimpleDocTemplate(filepath, pagesize=letter)
                styles = getSampleStyleSheet()
                story = []
                story.append(Paragraph(f"Laporan Rekapitulasi Gaji Bulan {month} Tahun {year}", styles['Title']))
                story.append(Spacer(1, 0.2 * inch))
                data = [["Nama Karyawan", "Gaji Pokok", "Total Tunjangan/Bonus", "Total Gaji Bersih"]] + report_data
                table = Table(data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
                    ('GRID', (0, 0), (-1, -1), 1, 'black'),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ]))
                story.append(table)
                doc.build(story)
                QMessageBox.information(self, "Berhasil", "Laporan gaji berhasil diekspor ke PDF!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal mengekspor laporan gaji ke PDF: {e}")

    def process_payroll(self):
        month = int(self.payroll_month_combo.currentText())
        year = int(self.payroll_year_combo.currentText())

        reply = QMessageBox.question(self, 'Konfirmasi Penggajian', 
                                     f"Anda yakin ingin memproses gaji untuk bulan {month}/{year}? Ini akan membuat slip gaji untuk semua karyawan.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.No:
            return

        employees = self.db.get_all_employees()
        processed_count = 0

        # Create a directory for payslips if it doesn't exist
        payslip_dir = os.path.join('resources', 'payslips')
        if not os.path.exists(payslip_dir):
            os.makedirs(payslip_dir)

        for employee_id, _, name, _, _, basic_salary, _, _ in employees:
            components = self.db.get_salary_components(employee_id, month, year)
            attendance_records = self.db.get_attendance(employee_id, 
                                                      QDate(year, month, 1).toString("yyyy-MM-dd"), 
                                                      QDate(year, month, QDate(year, month, 1).daysInMonth()).toString("yyyy-MM-dd"))

            total_allowances_bonuses = 0.0
            total_deductions_taxes = 0.0
            total_alpha_days = 0
            days_in_month = QDate(year, month, 1).daysInMonth()

            for comp_id, emp_id, comp_type, amount, comp_month, comp_year in components:
                if comp_type in ["Tunjangan", "Lembur", "Bonus"]:
                    total_allowances_bonuses += amount
                elif comp_type in ["Potongan", "Pajak", "Asuransi"]:
                    total_deductions_taxes += amount
            
            # Calculate deductions based on attendance
            for record in attendance_records:
                if record[5] == "Alpha": # Assuming index 5 is status
                    total_alpha_days += 1
            
            # Simple deduction for Alpha days (e.g., basic_salary / days_in_month * alpha_days)
            deduction_for_alpha = 0.0
            if days_in_month > 0:
                deduction_for_alpha = (basic_salary / days_in_month) * total_alpha_days
            
            # Add attendance deduction to total_deductions_taxes
            total_deductions_taxes += deduction_for_alpha

            total_gross_salary = basic_salary + total_allowances_bonuses
            total_net_salary = total_gross_salary - total_deductions_taxes

            # Generate PDF Payslip
            pdf_filename = f"slip_gaji_{name.replace(' ','_')}_{month}_{year}.pdf"
            pdf_filepath = os.path.join(payslip_dir, pdf_filename)
            self.generate_payslip_pdf(name, month, year, basic_salary, components, 
                                      total_net_salary, pdf_filepath, attendance_records, deduction_for_alpha)
            
            # Store processed payslip info in DB
            self.db.add_processed_payslip(employee_id, month, year, total_net_salary, pdf_filepath)
            processed_count += 1

        QMessageBox.information(self, "Berhasil", f"{processed_count} slip gaji berhasil diproses dan dibuat!")
        self.load_processed_payslips()

    def generate_payslip_pdf(self, employee_name, month, year, basic_salary, components, net_salary, filepath, attendance_records, deduction_for_alpha):
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        title_style = styles['h1']
        normal_style = styles['Normal']
        right_style = ParagraphStyle(name='RightAlign', alignment=TA_RIGHT)
        center_style = ParagraphStyle(name='CenterAlign', alignment=TA_CENTER)

        story = []

        story.append(Paragraph("SLIP GAJI KARYAWAN", center_style))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(f"Bulan: {month} Tahun: {year}", center_style))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph(f"Nama Karyawan: {employee_name}", normal_style))
        story.append(Paragraph(f"Gaji Pokok: Rp {basic_salary:,.2f}", normal_style))
        story.append(Spacer(1, 0.1 * inch))

        # Components Table
        data = [['Tipe Komponen', 'Jumlah']]
        for comp_id, emp_id, comp_type, amount, comp_month, comp_year in components:
            data.append([comp_type, f"Rp {amount:,.2f}"])
        
        # Add attendance deduction to components table for clarity
        if deduction_for_alpha > 0:
            data.append(['Potongan Absensi (Alpha)', f"Rp {deduction_for_alpha:,.2f}"])

        # Add a total row
        data.append(['<b>Total Gaji Bersih</b>', f'<b>Rp {net_salary:,.2f}</b>'])

        table = Table(data, colWidths=[3.5 * inch, 2.0 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), '#CCCCCC'),
            ('GRID', (0, 0), (-1, -1), 1, 'black'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Bold total row
            ('BACKGROUND', (0, -1), (-1, -1), '#EEEEEE'), # Grey background for total row
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

        # Attendance Summary in PDF
        total_days = QDate(year, month, 1).daysInMonth()
        hadir_days = sum(1 for r in attendance_records if r[5] == "Hadir")
        sakit_days = sum(1 for r in attendance_records if r[5] == "Sakit")
        izin_days = sum(1 for r in attendance_records if r[5] == "Izin")
        cuti_days = sum(1 for r in attendance_records if r[5] == "Cuti")
        alpha_days = sum(1 for r in attendance_records if r[5] == "Alpha")

        story.append(Paragraph("Ringkasan Absensi:", normal_style))
        story.append(Paragraph(f"Total Hari Kerja Bulan Ini: {total_days} hari", normal_style))
        story.append(Paragraph(f"Hadir: {hadir_days} hari", normal_style))
        story.append(Paragraph(f"Sakit: {sakit_days} hari", normal_style))
        story.append(Paragraph(f"Izin: {izin_days} hari", normal_style))
        story.append(Paragraph(f"Cuti: {cuti_days} hari", normal_style))
        story.append(Paragraph(f"Alpha: {alpha_days} hari", normal_style))
        story.append(Spacer(1, 0.5 * inch))

        story.append(Paragraph("Hormat kami,", right_style))
        story.append(Paragraph("Admin Perusahaan", right_style))

        doc.build(story)

    def load_processed_payslips(self):
        self.payslip_table.setRowCount(0)
        processed_payslips = self.db.get_all_processed_payslips()
        for row_num, payslip in enumerate(processed_payslips):
            self.payslip_table.insertRow(row_num)
            # payslip: pp.id, e.name, pp.month, pp.year, pp.net_salary, pp.pdf_path
            self.payslip_table.setItem(row_num, 0, QTableWidgetItem(str(payslip[1])))
            self.payslip_table.setItem(row_num, 1, QTableWidgetItem(str(payslip[2])))
            self.payslip_table.setItem(row_num, 2, QTableWidgetItem(str(payslip[3])))
            self.payslip_table.setItem(row_num, 3, QTableWidgetItem(f"{payslip[4]:,.2f}"))
            
            view_button = QPushButton("Lihat PDF")
            view_button.clicked.connect(lambda _, f=payslip[5]: self.open_pdf(f))
            self.payslip_table.setCellWidget(row_num, 4, view_button)

    def open_pdf(self, filepath):
        try:
            os.startfile(filepath)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Gagal membuka PDF: {e}")

    def record_check_in(self):
        try:
            employee_id = self.attendance_employee_combo.currentData()
            date = self.attendance_date_input.date().toString("yyyy-MM-dd")
            status = self.attendance_status_combo.currentText()
            check_in_time = datetime.now().strftime("%H:%M")

            if not employee_id:
                QMessageBox.warning(self, "Error", "Pilih karyawan terlebih dahulu.")
                return

            # Check if an attendance record for this employee and date already exists.
            self.db.cursor.execute('SELECT id FROM attendance WHERE employee_id = ? AND date = ?', (employee_id, date))
            if self.db.cursor.fetchone():
                QMessageBox.warning(self, "Error", f"Absensi untuk karyawan ini pada tanggal {date} sudah ada.")
                return

            if self.db.add_attendance(employee_id, date, check_in_time, None, status):
                QMessageBox.information(self, "Berhasil", f"Jam masuk untuk {self.attendance_employee_combo.currentText()} berhasil dicatat pada {check_in_time}.")
                self.load_admin_attendance()
            else:
                QMessageBox.warning(self, "Error", "Gagal mencatat jam masuk.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def record_check_out(self):
        try:
            employee_id = self.attendance_employee_combo.currentData()
            date = self.attendance_date_input.date().toString("yyyy-MM-dd")
            check_out_time = datetime.now().strftime("%H:%M")

            if not employee_id:
                QMessageBox.warning(self, "Error", "Pilih karyawan terlebih dahulu.")
                return

            if self.db.update_check_out(employee_id, date, check_out_time):
                 QMessageBox.information(self, "Berhasil", f"Jam keluar untuk {self.attendance_employee_combo.currentText()} berhasil dicatat pada {check_out_time}.")
                 self.load_admin_attendance()
            else:
                 QMessageBox.warning(self, "Error", "Gagal mencatat jam keluar. Pastikan sudah ada catatan jam masuk untuk karyawan dan tanggal yang dipilih, dan jam keluar belum diisi.")

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Terjadi kesalahan tak terduga: {e}")

    def load_admin_attendance(self):
        self.admin_attendance_table.setRowCount(0)
        all_attendance = self.db.get_all_attendance_with_employee_names()

        for row_num, record in enumerate(all_attendance):
            self.admin_attendance_table.insertRow(row_num)
            for col_num, data in enumerate(record):
                # Handle None values for check_in and check_out
                if data is None:
                    data = ''
                self.admin_attendance_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def clear_attendance_form(self):
        self.attendance_employee_combo.setCurrentIndex(0)
        self.attendance_date_input.setDate(QDate.currentDate())
        self.attendance_status_combo.setCurrentIndex(0)

    def load_attendance_employee_combo(self):
        self.attendance_employee_combo.clear()
        self.attendance_employee_combo.addItem("Pilih Karyawan", None) # Add a default empty item
        employees = self.db.get_all_employees()
        for emp_id, _, name, _, _, _, _, _ in employees:
            self.attendance_employee_combo.addItem(f"{name} ({emp_id})", emp_id) 