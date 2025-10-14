import sqlite3
import bcrypt
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database/payroll.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_default_admin()

    def create_tables(self):
        # Tabel Users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Tabel Karyawan
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nip TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                department TEXT NOT NULL,
                basic_salary REAL NOT NULL,
                join_date DATE NOT NULL,
                status TEXT NOT NULL
            )
        ''')

        # Tabel Komponen Gaji
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS salary_components (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                component_type TEXT NOT NULL,
                amount REAL NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        # Tabel Absensi
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER,
                date DATE NOT NULL,
                check_in TIME,
                check_out TIME,
                status TEXT NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        # Tabel Processed Payslips
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_payslips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                net_salary REAL NOT NULL,
                pdf_path TEXT NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(employee_id, month, year),
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        ''')

        self.conn.commit()

    def create_default_admin(self):
        # Check if admin user exists
        self.cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if not self.cursor.fetchone():
            # Create default admin user
            self.add_user('admin', 'admin123', 'admin')
            print("Default admin user created successfully!")

    def add_user(self, username, password, role):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        try:
            self.cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, hashed.decode('utf-8'), role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_user(self, username, password):
        self.cursor.execute('SELECT password, role FROM users WHERE username = ?', (username,))
        result = self.cursor.fetchone()
        if result:
            stored_password, role = result
            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                return role
        return None

    def add_employee(self, nip, name, position, department, basic_salary, join_date, status):
        try:
            self.cursor.execute('''
                INSERT INTO employees (nip, name, position, department, basic_salary, join_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nip, name, position, department, basic_salary, join_date, status))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_employee(self, employee_id=None, nip=None):
        if employee_id:
            self.cursor.execute('SELECT * FROM employees WHERE id = ?', (employee_id,))
        elif nip:
            self.cursor.execute('SELECT * FROM employees WHERE nip = ?', (nip,))
        return self.cursor.fetchone()

    def get_all_employees(self):
        self.cursor.execute('SELECT id, nip, name, position, department, basic_salary, join_date, status FROM employees')
        return self.cursor.fetchall()

    def update_employee(self, employee_id, nip, name, position, department, basic_salary, join_date, status):
        try:
            self.cursor.execute('''
                UPDATE employees
                SET nip = ?, name = ?, position = ?, department = ?, basic_salary = ?, join_date = ?, status = ?
                WHERE id = ?
            ''', (nip, name, position, department, basic_salary, join_date, status, employee_id))
            self.conn.commit()
            
            if self.cursor.rowcount == 0:
                print(f"[DEBUG] Database: Update employee (ID: {employee_id}) tidak mempengaruhi baris. Mungkin ID tidak ditemukan.")
                return False # Indicate failure if no rows were updated
            
            print(f"[DEBUG] Database: Menerima Basic Salary untuk update: {basic_salary}, Baris terpengaruh: {self.cursor.rowcount}")
            return True
        except sqlite3.IntegrityError:
            print(f"[DEBUG] Database: IntegrityError saat update employee dengan NIP: {nip}")
            return False
        except Exception as e:
            print(f"[DEBUG] Database: Error tak terduga saat update employee: {e}")
            return False

    def delete_employee(self, employee_id):
        self.cursor.execute('DELETE FROM employees WHERE id = ?', (employee_id,))
        self.conn.commit()
        return True

    def add_salary_component(self, employee_id, component_type, amount, month, year):
        self.cursor.execute('''
            INSERT INTO salary_components (employee_id, component_type, amount, month, year)
            VALUES (?, ?, ?, ?, ?)
        ''', (employee_id, component_type, amount, month, year))
        self.conn.commit()

    def get_all_salary_components(self):
        self.cursor.execute('SELECT sc.id, e.name, sc.component_type, sc.amount, sc.month, sc.year FROM salary_components sc JOIN employees e ON sc.employee_id = e.id')
        return self.cursor.fetchall()

    def get_salary_components(self, employee_id, month, year):
        self.cursor.execute('''
            SELECT * FROM salary_components 
            WHERE employee_id = ? AND month = ? AND year = ?
        ''', (employee_id, month, year))
        return self.cursor.fetchall()

    def add_attendance(self, employee_id, date, check_in, check_out, status):
        try:
            self.cursor.execute('''
                INSERT INTO attendance (employee_id, date, check_in, check_out, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (employee_id, date, check_in, check_out, status))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DEBUG] Database: Error adding attendance: {e}")
            return False

    def get_attendance(self, employee_id, start_date, end_date):
        self.cursor.execute('''
            SELECT * FROM attendance 
            WHERE employee_id = ? AND date BETWEEN ? AND ?
        ''', (employee_id, start_date, end_date))
        return self.cursor.fetchall()

    def get_all_attendance_with_employee_names(self):
        self.cursor.execute('''
            SELECT a.id, e.name, a.date, a.check_in, a.check_out, a.status
            FROM attendance a JOIN employees e ON a.employee_id = e.id
            ORDER BY a.date DESC
        ''')
        return self.cursor.fetchall()

    def update_attendance(self, attendance_id, employee_id, date, check_in, check_out, status):
        try:
            self.cursor.execute('''
                UPDATE attendance
                SET employee_id = ?, date = ?, check_in = ?, check_out = ?, status = ?
                WHERE id = ?
            ''', (employee_id, date, check_in, check_out, status, attendance_id))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DEBUG] Database: Error updating attendance: {e}")
            return False

    def delete_attendance(self, attendance_id):
        try:
            self.cursor.execute('DELETE FROM attendance WHERE id = ?', (attendance_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DEBUG] Database: Error deleting attendance: {e}")
            return False

    def update_salary_component(self, component_id, employee_id, component_type, amount, month, year):
        try:
            self.cursor.execute('''
                UPDATE salary_components
                SET employee_id = ?, component_type = ?, amount = ?, month = ?, year = ?
                WHERE id = ?
            ''', (employee_id, component_type, amount, month, year, component_id))
            self.conn.commit()
            return True
        except Exception:
            return False

    def delete_salary_component(self, component_id):
        self.cursor.execute('DELETE FROM salary_components WHERE id = ?', (component_id,))
        self.conn.commit()
        return True

    def add_processed_payslip(self, employee_id, month, year, net_salary, pdf_path):
        try:
            self.cursor.execute('''
                INSERT INTO processed_payslips (employee_id, month, year, net_salary, pdf_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (employee_id, month, year, net_salary, pdf_path))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_processed_payslips_for_employee(self, employee_id):
        self.cursor.execute('SELECT * FROM processed_payslips WHERE employee_id = ? ORDER BY year DESC, month DESC', (employee_id,))
        return self.cursor.fetchall()

    def get_all_processed_payslips(self):
        self.cursor.execute('''
            SELECT pp.id, e.name, pp.month, pp.year, pp.net_salary, pp.pdf_path 
            FROM processed_payslips pp JOIN employees e ON pp.employee_id = e.id
            ORDER BY pp.year DESC, pp.month DESC
        ''')
        return self.cursor.fetchall()

    def update_check_out(self, employee_id, date, check_out_time):
        try:
            self.cursor.execute('''
                UPDATE attendance
                SET check_out = ?
                WHERE employee_id = ? AND date = ? AND check_out IS NULL
            ''', (check_out_time, employee_id, date))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                return True
            else:
                return False # No record was updated
        except Exception as e:
            print(f"[DEBUG] Database: Error updating check_out: {e}")
            return False

    def close(self):
        self.conn.close() 