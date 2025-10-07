# Payroll System

Aplikasi manajemen penggajian karyawan berbasis Python dan SQLite.  
Membantu HR dalam mengelola data karyawan, absensi, komponen gaji, dan pembuatan slip gaji secara otomatis.

## Fitur Utama

- Manajemen data karyawan (CRUD)
- Pengelolaan absensi (check-in, check-out, status)
- Pengaturan komponen gaji (tunjangan, potongan, dsb)
- Proses dan cetak slip gaji (PDF)
- Sistem login multi-user (admin & user)
- Riwayat slip gaji karyawan

## Instalasi

1. **Clone repository:**
   ```sh
   git clone https://github.com/DillanINF/PAYROLL_SYSTEM.git
   cd PAYROLL_SYSTEM
   ```

2. **Masuk ke folder source:**
   ```sh
   cd src
   ```

3. **Buat folder database (jika belum ada):**
   ```sh
   mkdir database
   ```

4. **Install dependencies:**
   ```sh
   pip install -r ../requirements.txt
   ```

5. **Jalankan aplikasi:**
   ```sh
   python main.py
   ```

## Login Default

- **Username:** admin  
- **Password:** admin123

Akun admin default akan otomatis dibuat saat aplikasi pertama kali dijalankan.

## Struktur Folder

```
PAYROLL_SYSTEM/
│
├── src/
│   ├── main.py
│   ├── database.py
│   ├── ... (file modul lain)
│   └── database/
│       └── payroll.db
├── requirements.txt
└── README.md
```

## Lisensi

MIT License

---

> Dibuat untuk kebutuhan pembelajaran dan pengelolaan payroll sederhana.
