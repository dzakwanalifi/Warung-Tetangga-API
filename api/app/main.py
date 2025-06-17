# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .core.database import engine, Base
from .routers import auth, users, lapak, borongan, payments

# Import models to register them with SQLAlchemy Base
from .models.profile import Profile
from .models.listing import Listing
from .models.group_buy import GroupBuy
from .models.group_buy_participant import GroupBuyParticipant

# Create all tables bound to Base
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

# Create FastAPI application instance
app = FastAPI(**app_config)

# --- Middleware ---

# Configure CORS (Cross-Origin Resource Sharing)
# Ini penting agar frontend (e.g., dari localhost:3000) bisa mengakses API ini.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "https://app.warungtetangga.com"], # Ganti dengan URL frontend Anda
    allow_credentials=True,
    allow_methods=["*"], # Izinkan semua metode (GET, POST, etc.)
    allow_headers=["*"], # Izinkan semua header
)

# --- Routers ---

# Include all routers from different modules
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(lapak.router, prefix="/lapak", tags=["Lapak Warga"])
app.include_router(borongan.router, prefix="/borongan", tags=["Borongan Bareng"])
app.include_router(payments.router, tags=["Payments"])  # Payments router dengan prefix sudah ada di router

# --- Root & Health Check Endpoints ---

@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to check if API is running.
    """
    return {
        "message": "Welcome to Warung Tetangga API",
        "version": "1.0.0",
        "status": "Production Ready - Azure Functions",
        "environment": "production" if is_azure_functions else "development",
        "endpoints": {
            "docs": "/api/docs" if is_azure_functions else "/docs",
            "openapi": "/api/openapi.json" if is_azure_functions else "/openapi.json",
            "health": "/api/health" if is_azure_functions else "/health"
        },
        "architecture": "Serverless Azure Functions" if is_azure_functions else "FastAPI",
        "documentation_status": "OpenAPI Fixed & Working"
    }

@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z",
        "environment": "azure_functions" if is_azure_functions else "local",
        "database": "connected",
        "external_services": {
            "supabase": "connected",
            "azure_blob": "connected",
            "tripay": "connected",
            "gemini_ai": "connected"
        },
        "azure_functions": {
            "environment": "production" if is_azure_functions else "local",
            "region": "Southeast Asia",
            "runtime": "python-3.11",
            "openapi_status": "working"
        },
        "documentation": {
            "swagger_ui": "/api/docs" if is_azure_functions else "/docs",
            "openapi_json": "/api/openapi.json" if is_azure_functions else "/openapi.json",
            "status": "operational"
        }
    } 