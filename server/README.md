# ⚙️ Server (Backend) - URL Shortener

Ini adalah direktori *backend* untuk proyek URL Shortener & QR Code Generator. Backend ini dibangun menggunakan arsitektur modern berbasis Python.

## 🌟 Fitur Utama
- **Autentikasi:** Menggunakan JWT (JSON Web Tokens) untuk registrasi dan login.
- **Manajemen URL:** Membuat, mengedit, dan menghapus tautan singkat (Short URL).
- **QR Code Generator:** Membuat QR Code otomatis untuk setiap tautan yang dibuat dan mengunggahnya ke Cloudflare R2 / AWS S3.
- **Analytics:** Melacak jumlah klik, *user-agent* (browser/perangkat), dan IP untuk analitik tautan.

## 🛠️ Tech Stack
- **Framework:** FastAPI
- **ORM:** SQLModel
- **Database:** PostgreSQL (Hosted on Supabase)
- **Object Storage:** Cloudflare R2 / S3 (boto3)
- **Image Generation:** qrcode

---

## 📌 Prasyarat Instalasi

Pastikan kamu sudah menginstal **Python 3.9+** di komputermu. Semua perintah di bawah ini harus dijalankan di dalam direktori `server`.

### 1. Setup Virtual Environment (Wajib)
Buat dan aktifkan *virtual environment* agar *dependency* backend tidak bentrok dengan *project* lain.
```bash
python -m venv venv

# Aktivasi di Windows (PowerShell)
.\venv\Scripts\activate

# Aktivasi di macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔑 Konfigurasi Environment Variables (`.env`)

Buat file bernama `.env` di dalam folder `server` ini. File ini wajib ada agar aplikasi bisa terhubung ke Database dan Storage. **(JANGAN PERNAH MENGUNGGAH FILE INI KE GITHUB)**.

Contoh format `.env`:
```env
# Koneksi Database Supabase (Gunakan Connection Pooling / Mode Transaction)
DATABASE_URL=postgresql://[user]:[password]@[pooler_domain]:6543/postgres

# Konfigurasi JWT (Gunakan string random 64 karakter)
JWT_SECRET_KEY=rahasia_super_kuat_jangan_disebar
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# Base URL Aplikasi Backend
BASE_URL=http://127.0.0.1:8000

# Konfigurasi Cloudflare R2 / S3
R2_ENDPOINT_URL=https://<account_id>.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_BUCKET_NAME=your_bucket_name
R2_PUBLIC_URL=https://pub-xxxxxx.r2.dev
```

---

## 🚀 Cara Menjalankan Server

Pastikan *virtual environment* kamu dalam keadaan **aktif** `(venv)`, lalu jalankan perintah Uvicorn:

```bash
uvicorn app.main:app --reload
```
Server akan berjalan di `http://127.0.0.1:8000`. Flag `--reload` akan otomatis melakukan *restart* jika ada perubahan pada kode Python.

---

## 🧪 Testing (Pytest)

Aplikasi ini menggunakan `pytest` dan `httpx` untuk *automated testing*. Pastikan *virtual environment* kamu dalam keadaan aktif.
```bash
.\venv\Scripts\activate
```

### 1. Menjalankan Seluruh Test
```bash
pytest -v
```

### 2. Menjalankan File Test Tertentu
```bash
pytest tests/test_auth.py -v
pytest tests/test_url.py -v
```
---

## 📖 Dokumentasi API (Swagger UI)

Kehebatan FastAPI adalah dokumentasi API yang *auto-generated*. Kamu bisa langsung mencoba dan melakukan *testing endpoint* (termasuk Login dan CRUD) langsung dari browser.

Buka browser dan kunjungi:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**