# 🔗 URL Shortener & QR Code Generator (Fullstack)

Selamat datang di repositori proyek **URL Shortener & QR Code Generator**. Proyek ini adalah aplikasi *fullstack* yang dirancang untuk memendekkan tautan (URL) panjang menjadi URL singkat, sekaligus memiliki fitur *generate* QR Code untuk mempermudah akses tautan tersebut.

Repositori ini menggunakan struktur **Monorepo**, di mana kode untuk *frontend* (Client) dan *backend* (Server) disimpan bersama di dalam satu tempat untuk mempermudah pengembangan dan sinkronisasi.

---

## 📁 Struktur Folder

Proyek ini dibagi menjadi dua bagian utama:

```text
UrlShortener/
│
├── client/         # 💻 Frontend App
│   # Berisi kode antarmuka pengguna (User Interface).
│   # Dibangun menggunakan framework modern (React / Next.js / Vue).
│
├── server/         # ⚙️ Backend App (API)
│   # Berisi kode server, logika bisnis, dan koneksi ke database.
│   # Dibangun menggunakan Python (FastAPI), SQLModel, dan PostgreSQL.
│
├── .gitignore      # Daftar file yang tidak akan di-push ke Github
└── README.md       # Dokumentasi utama proyek (File ini)
```

---

## 🚀 Teknologi yang Digunakan

### Backend (`/server`)
- **Framework:** FastAPI (Python)
- **ORM:** SQLModel (SQLAlchemy & Pydantic)
- **Database:** PostgreSQL (via Supabase)
- **Authentication:** JWT (JSON Web Tokens)
- **Storage:** Cloudflare R2 / AWS S3 (untuk menyimpan file gambar QR Code)
- **QR Code:** Library `qrcode` Python

### Frontend (`/client`)
- *(Folder ini disiapkan untuk aplikasi frontend web modern, misalnya React, Next.js, atau Vue.js).*

---

## 🛠️ Panduan Menjalankan Proyek (Local Development)

Karena ini adalah arsitektur Monorepo, kamu perlu menjalankan `client` dan `server` di dua terminal yang berbeda.

### 1. Menjalankan Backend (Server)
Buka terminal baru, lalu navigasikan ke folder `server` dan aktifkan Virtual Environment (*venv*).

```bash
# Masuk ke direktori server
cd server

# Aktifkan virtual environment (Windows)
.\venv\Scripts\activate

# Install dependencies (Jika belum)
pip install -r requirements.txt

# Jalankan server dengan Uvicorn
uvicorn app.main:app --reload
```
Server backend akan berjalan di: `http://127.0.0.1:8000`

### 2. Menjalankan Frontend (Client)
Buka tab terminal kedua, lalu navigasikan ke folder `client`.

```bash
# Masuk ke direktori client
cd client

# Install dependensi Node.js
npm install

# Jalankan server development
npm run dev
```
