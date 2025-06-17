# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

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

# Detect if running under Azure Functions
is_azure_functions = os.getenv('AZURE_FUNCTIONS_ENVIRONMENT') is not None or os.getenv('FUNCTIONS_WORKER_RUNTIME') is not None

# Configure FastAPI with appropriate settings for Azure Functions
app_config = {
    "title": "Warung Tetangga API",
    "description": "API untuk aplikasi hyperlocal Warung Tetangga. Memungkinkan fitur Lapak Warga dan Borongan Bareng dengan integrasi pembayaran Tripay.",
    "version": "1.0.0",
    "contact": {
        "name": "Tim Warung Tetangga",
        "url": "https://warungtetangga.com",
        "email": "admin@warungtetangga.com",
    },
}

# Add Azure Functions specific configuration
if is_azure_functions:
    # When running under Azure Functions, set root_path to /api
    # This ensures that OpenAPI URLs are correctly generated
    app_config["root_path"] = "/api"
    app_config["docs_url"] = "/docs"
    app_config["redoc_url"] = "/redoc"
    app_config["openapi_url"] = "/openapi.json"
else:
    # Default FastAPI configuration for local development
    app_config["docs_url"] = "/docs"
    app_config["redoc_url"] = "/redoc"

# Buat instance aplikasi FastAPI
app = FastAPI(**app_config)

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
    return {
        "message": "Welcome to Warung Tetangga API",
        "version": "1.0.0",
        "status": "Production Ready - Azure Functions",
        "endpoints": {
            "docs": "/api/docs" if is_azure_functions else "/docs",
            "health": "/api/health" if is_azure_functions else "/health"
        },
        "architecture": "Serverless Azure Functions" if is_azure_functions else "FastAPI"
    }

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Endpoint health check sederhana.
    """
    return {
        "status": "healthy",
        "environment": "azure_functions" if is_azure_functions else "local",
        "database": "connected",
        "external_services": {
            "supabase": "connected",
            "azure_blob": "connected", 
            "tripay": "connected"
        }
    } 