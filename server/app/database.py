import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# jembatan komunikasi ke database
engine = create_engine(DATABASE_URL, echo=False)

# fungsi untuk membuat tabel otomatis (npx prisma db push)
def create_db_and_tables():
    # baca semua class model yang memiliki parameter table=True, lalu buat tabelnya di database
    SQLModel.metadata.create_all(engine)


# Dependency Injection (Middleware Database)
# Membuat koneksi database baru di awal request, dan secara otomatis menutup koneksinya saat response sudah dikirim
# agar bebas dari memory leak
def get_session():
    with Session(engine) as session:
        yield session
