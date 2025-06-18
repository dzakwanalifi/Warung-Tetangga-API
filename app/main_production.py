# app/main_production.py
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flag to check if database is available
DB_AVAILABLE = False
engine = None
Base = None

# Try to initialize database connection
try:
    if not os.environ.get("SKIP_DB_INIT"):
        from .core.database import engine as db_engine, Base as db_base
        from .core.database import SessionLocal
        engine = db_engine
        Base = db_base
        
        # Test connection
        with engine.connect() as conn:
            logger.info("✅ Database connection successful")
            DB_AVAILABLE = True
            
        # Import models to register them with SQLAlchemy Base
        from .models.profile import Profile
        from .models.listing import Listing
        from .models.group_buy import GroupBuy
        from .models.group_buy_participant import GroupBuyParticipant
        
        # Create tables if database is available
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
    else:
        logger.info("ℹ️ Database initialization skipped (SKIP_DB_INIT=true)")
        
except Exception as e:
    logger.warning(f"⚠️ Database not available: {e}")
    DB_AVAILABLE = False

# Create FastAPI instance
app = FastAPI(
    title="Warung Warga API",
    description="API untuk aplikasi hyperlocal Warung Warga. Memungkinkan fitur Lapak Warga dan Borongan Bareng dengan integrasi pembayaran Tripay.",
    version="1.0.0",
    contact={
        "name": "Tim Warung Warga",
        "url": "https://warungwarga.com",
        "email": "admin@warungwarga.com",
    },
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "https://app.warungwarga.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers only if database is available
if DB_AVAILABLE:
    try:
        from .routers import auth, users, lapak, borongan, payments
        app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
        app.include_router(users.router, prefix="/users", tags=["Users"])
        app.include_router(lapak.router, prefix="/lapak", tags=["Lapak Warga"])
        app.include_router(borongan.router, prefix="/borongan", tags=["Borongan Bareng"])
        app.include_router(payments.router, tags=["Payments"])
        logger.info("✅ All routers included successfully")
    except Exception as e:
        logger.error(f"❌ Failed to include routers: {e}")
        DB_AVAILABLE = False

# Root endpoint
@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint root untuk mengecek apakah API berjalan.
    """
    status = "connected" if DB_AVAILABLE else "database_unavailable"
    return {
        "message": "Welcome to Warung Warga API v1.0.0",
        "status": status,
        "database_available": DB_AVAILABLE
    }

# Health check endpoint
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Endpoint health check dengan informasi database.
    """
    return {
        "status": "ok",
        "database_available": DB_AVAILABLE,
        "environment": "production" if not os.environ.get("SKIP_DB_INIT") else "minimal"
    }

# Database status endpoint
@app.get("/db-status", tags=["Database"])
async def database_status():
    """
    Endpoint untuk mengecek status database.
    """
    if not DB_AVAILABLE:
        return {
            "database_available": False,
            "message": "Database connection not available",
            "available_endpoints": ["/", "/health", "/db-status", "/docs"]
        }
    
    try:
        # Test database connection
        with engine.connect() as conn:
            return {
                "database_available": True,
                "connection_status": "active",
                "message": "Database connection is working"
            }
    except Exception as e:
        return {
            "database_available": False,
            "connection_status": "failed",
            "error": str(e)
        }

# API info endpoint
@app.get("/info", tags=["Info"])
async def api_info():
    """
    API information endpoint.
    """
    endpoints = ["/", "/health", "/db-status", "/info", "/docs"]
    
    if DB_AVAILABLE:
        endpoints.extend([
            "/auth/*", "/users/*", "/lapak/*", 
            "/borongan/*", "/payments/*"
        ])
    
    return {
        "title": "Warung Warga API",
        "version": "1.0.0",
        "mode": "production",
        "database_available": DB_AVAILABLE,
        "endpoints": endpoints,
        "status": "operational"
    } 