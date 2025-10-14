import sqlite3

# Path ke database
DB_PATH = 'database/payroll.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Hapus data dari tabel-tabel utama
cursor.execute('DELETE FROM attendance;')
cursor.execute('DELETE FROM salary_components;')
cursor.execute('DELETE FROM processed_payslips;')
cursor.execute('DELETE FROM employees;')

conn.commit()
conn.close()

print('Semua data karyawan, absensi, gaji, dan slip telah dihapus. User admin tetap ada.') 