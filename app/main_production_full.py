import os
import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

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

# Database dependency with graceful handling
def get_db():
    if not DB_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail={
                "error": "Database not available",
                "message": "This endpoint requires database connection which is currently unavailable",
                "available_endpoints": ["/", "/health", "/db-status", "/info", "/docs"]
            }
        )
    
    from .core.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Always include routers, but they will handle database unavailability gracefully
try:
    from .routers import auth, users, lapak, borongan, payments
    
    # Include all routers regardless of database status
    app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/users", tags=["Users"])
    app.include_router(lapak.router, prefix="/lapak", tags=["Lapak Warga"])
    app.include_router(borongan.router, prefix="/borongan", tags=["Borongan Bareng"])
    app.include_router(payments.router, tags=["Payments"])
    logger.info("✅ All routers included successfully")
    
except Exception as e:
    logger.error(f"❌ Failed to include routers: {e}")
    
    # Create mock routers if real ones fail
    from fastapi import APIRouter
    
    # Mock Auth Router
    mock_auth = APIRouter(prefix="/auth", tags=["Authentication"])
    
    @mock_auth.post("/register")
    async def mock_register():
        return {"error": "Database not available", "endpoint": "register", "status": "unavailable"}
    
    @mock_auth.post("/login")
    async def mock_login():
        return {"error": "Database not available", "endpoint": "login", "status": "unavailable"}
    
    # Mock Users Router
    mock_users = APIRouter(prefix="/users", tags=["Users"])
    
    @mock_users.get("/users/me")
    async def mock_read_users_me():
        return {"error": "Database not available", "endpoint": "users/me", "status": "unavailable"}
    
    @mock_users.put("/users/me")
    async def mock_update_users_me():
        return {"error": "Database not available", "endpoint": "users/me", "status": "unavailable"}
    
    # Mock Lapak Router
    mock_lapak = APIRouter(prefix="/lapak", tags=["Lapak Warga"])
    
    @mock_lapak.post("/analyze")
    async def mock_analyze_image():
        return {"error": "Database not available", "endpoint": "analyze", "status": "unavailable"}
    
    @mock_lapak.post("/")
    async def mock_create_lapak():
        return {"error": "Database not available", "endpoint": "create_lapak", "status": "unavailable"}
    
    @mock_lapak.get("/nearby")
    async def mock_get_lapak_nearby():
        return {"error": "Database not available", "endpoint": "nearby", "status": "unavailable"}
    
    @mock_lapak.get("/{listing_id}")
    async def mock_get_lapak_detail(listing_id: str):
        return {"error": "Database not available", "endpoint": f"lapak/{listing_id}", "status": "unavailable"}
    
    @mock_lapak.put("/{listing_id}")
    async def mock_update_lapak(listing_id: str):
        return {"error": "Database not available", "endpoint": f"lapak/{listing_id}", "status": "unavailable"}
    
    # Mock Borongan Router
    mock_borongan = APIRouter(prefix="/borongan", tags=["Borongan Bareng"])
    
    @mock_borongan.get("/")
    async def mock_get_active_borongan():
        return {"error": "Database not available", "endpoint": "borongan", "status": "unavailable"}
    
    @mock_borongan.post("/")
    async def mock_create_borongan():
        return {"error": "Database not available", "endpoint": "create_borongan", "status": "unavailable"}
    
    @mock_borongan.get("/{borongan_id}")
    async def mock_get_borongan_detail(borongan_id: str):
        return {"error": "Database not available", "endpoint": f"borongan/{borongan_id}", "status": "unavailable"}
    
    @mock_borongan.post("/{group_buy_id}/join")
    async def mock_join_borongan(group_buy_id: str):
        return {"error": "Database not available", "endpoint": f"join/{group_buy_id}", "status": "unavailable"}
    
    # Mock Payments Router
    mock_payments = APIRouter(tags=["Payments"])
    
    @mock_payments.post("/payments/tripay/webhook")
    async def mock_tripay_webhook():
        return {"error": "Database not available", "endpoint": "tripay_webhook", "status": "unavailable"}
    
    @mock_payments.get("/payments/tripay/status/{participant_id}")
    async def mock_check_payment_status(participant_id: str):
        return {"error": "Database not available", "endpoint": f"payment_status/{participant_id}", "status": "unavailable"}
    
    @mock_payments.get("/payments/methods")
    async def mock_get_payment_methods():
        return {"error": "Database not available", "endpoint": "payment_methods", "status": "unavailable"}
    
    @mock_payments.get("/payments/status/{participant_id}")
    async def mock_get_payment_status(participant_id: str):
        return {"error": "Database not available", "endpoint": f"payment_status/{participant_id}", "status": "unavailable"}
    
    # Include mock routers
    app.include_router(mock_auth)
    app.include_router(mock_users)
    app.include_router(mock_lapak)
    app.include_router(mock_borongan)
    app.include_router(mock_payments)
    logger.info("✅ Mock routers included due to router import failure")

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
            "note": "All API endpoints are still accessible but will return 'database unavailable' responses",
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
    all_endpoints = [
        "/", "/health", "/db-status", "/info", "/docs",
        "/auth/register", "/auth/login",
        "/users/users/me",
        "/lapak/analyze", "/lapak", "/lapak/nearby", "/lapak/{listing_id}",
        "/borongan/", "/borongan/{borongan_id}", "/borongan/{group_buy_id}/join",
        "/payments/tripay/webhook", "/payments/tripay/status/{participant_id}",
        "/payments/methods", "/payments/status/{participant_id}"
    ]
    
    return {
        "title": "Warung Warga API",
        "version": "1.0.0",
        "mode": "production_full",
        "database_available": DB_AVAILABLE,
        "endpoints": all_endpoints,
        "status": "operational",
        "note": "All endpoints are available. Database-dependent endpoints will return appropriate error messages if database is unavailable."
    } 