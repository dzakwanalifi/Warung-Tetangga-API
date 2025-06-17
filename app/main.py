# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.database import engine, Base  # <-- Impor Base
from .routers import auth, users, lapak, borongan, payments  # <-- Impor router payments

# Import models to register them with SQLAlchemy Base
from .models.profile import Profile
from .models.listing import Listing
from .models.group_buy import GroupBuy
from .models.group_buy_participant import GroupBuyParticipant

# Membuat semua tabel yang terikat pada Base
# Ini sebaiknya dipindahkan ke skrip migrasi (e.g., Alembic) untuk produksi,
# tapi untuk MVP ini sudah cukup.
Base.metadata.create_all(bind=engine)

# Buat instance aplikasi FastAPI
app = FastAPI(
    title="Warung Tetangga API",
    description="API untuk aplikasi hyperlocal Warung Tetangga. Memungkinkan fitur Lapak Warga dan Borongan Bareng dengan integrasi pembayaran Tripay.",
    version="1.0.0",
    # Opsional: Menambahkan informasi kontak dan lisensi di docs
    contact={
        "name": "Tim Warung Tetangga",
        "url": "https://warungtetangga.com",
        "email": "admin@warungtetangga.com",
    },
)

# --- Middleware ---

# Konfigurasi CORS (Cross-Origin Resource Sharing)
# Ini penting agar frontend (e.g., dari localhost:3000) bisa mengakses API ini.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "https://app.warungtetangga.com"], # Ganti dengan URL frontend Anda
    allow_credentials=True,
    allow_methods=["*"], # Izinkan semua metode (GET, POST, etc.)
    allow_headers=["*"], # Izinkan semua header
)

# --- Routers ---

# Sertakan semua router dari modul yang berbeda
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(lapak.router, prefix="/lapak", tags=["Lapak Warga"])
app.include_router(borongan.router, prefix="/borongan", tags=["Borongan Bareng"])
app.include_router(payments.router, tags=["Payments"])  # Payments router dengan prefix sudah ada di router

# --- Endpoint Root & Health Check ---

@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint root untuk mengecek apakah API berjalan.
    """
    return {"message": "Welcome to Warung Tetangga API v1.0.0"}

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Endpoint health check sederhana.
    """
    return {"status": "ok"} 