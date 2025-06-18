# app/main_minimal.py
# Minimal FastAPI app for Azure Functions without database dependencies

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(
    title="Warung Warga API (Minimal)",
    description="Minimal API untuk testing Azure Functions deployment",
    version="1.0.0-minimal",
    contact={
        "name": "Tim Warung Warga",
        "url": "https://warungwarga.com",
        "email": "admin@warungwarga.com",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint to check if API is running.
    """
    return {"message": "Welcome to Warung Warga API v1.0.0 (Minimal Mode)", "status": "ok"}

# Health check endpoint
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok", "mode": "minimal", "message": "API is running successfully"}

# Test endpoint
@app.get("/test", tags=["Test"])
async def test_endpoint():
    """
    Test endpoint for validation.
    """
    return {
        "message": "Test endpoint working",
        "status": "success",
        "features": ["basic_routing", "cors_enabled", "json_responses"]
    }

# API info endpoint
@app.get("/info", tags=["Info"])
async def api_info():
    """
    API information endpoint.
    """
    return {
        "title": "Warung Warga API",
        "version": "1.0.0-minimal",
        "mode": "Azure Functions Minimal",
        "endpoints": ["/", "/health", "/test", "/info", "/docs"],
        "status": "operational"
    } 