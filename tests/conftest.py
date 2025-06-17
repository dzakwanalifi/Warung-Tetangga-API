# tests/conftest.py

import pytest
from sqlalchemy import create_engine, Column, String, Text, Numeric, Integer, DateTime, ForeignKey, DECIMAL, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import uuid
from datetime import datetime
from app.models.listing import Listing

# Create a test database using SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define test models for SQLite (without geospatial types)
TestBase = declarative_base()

class TestProfile(TestBase):
    __tablename__ = "profiles"
    
    id = Column(String, primary_key=True)  # Use String for UUID in SQLite
    full_name = Column(String, nullable=False)
    profile_picture_url = Column(String)
    address_text = Column(Text)
    # Remove geoalchemy2 dependency - use latitude/longitude separately for testing
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    reputation_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestListing(TestBase):
    __tablename__ = "listings"
    
    id = Column(String, primary_key=True)  # Use String for UUID in SQLite
    seller_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(precision=12, scale=2), nullable=False)
    unit = Column(String, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_urls = Column(Text)  # JSON stored as text in SQLite
    status = Column(String, default='available')
    # For testing, use separate lat/lon instead of PostGIS geometry
    latitude = Column(Numeric(precision=10, scale=7))
    longitude = Column(Numeric(precision=10, scale=7))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TestGroupBuy(TestBase):
    __tablename__ = "group_buys"

    id = Column(String, primary_key=True)  # Use String for SQLite compatibility
    supplier_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    
    target_quantity = Column(Integer, nullable=False)
    current_quantity = Column(Integer, nullable=False, default=0)
    
    deadline = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default='active')
    pickup_point_address = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now)

class TestGroupBuyParticipant(TestBase):
    __tablename__ = "group_buy_participants"

    id = Column(String, primary_key=True)  # Use String for SQLite compatibility
    group_buy_id = Column(String, ForeignKey("group_buys.id"), nullable=False)
    user_id = Column(String, ForeignKey("profiles.id"), nullable=False)
    
    quantity_ordered = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), nullable=False, default='pending')
    payment_method = Column(String(50), nullable=True)
    tripay_reference = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)

@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    """
    # Create all tables
    TestBase.metadata.create_all(bind=engine)
    
    # Create a new session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after each test for clean state
        TestBase.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Create a TestClient that uses the test database session.
    """
    from app.main import app
    from app.core.database import get_db
    
    # Override the get_db dependency to use our test session
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

@pytest.fixture
def test_user(db_session: Session):
    """
    Create a test user in the database with a location.
    """
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": "test@example.com"
    }
    
    # Create profile with location
    profile = TestProfile(
        id=user_id,
        full_name="Test User",
        latitude=-6.200000,  # Jakarta coordinates
        longitude=106.816666
    )
    db_session.add(profile)
    db_session.commit()
    
    return user_data

@pytest.fixture
def supplier_user(db_session: Session):
    """
    Create a supplier user in the database.
    """
    user_id = str(uuid.uuid4())
    user_data = {
        "id": user_id,
        "email": "supplier@example.com"
    }
    
    # Create profile
    profile = TestProfile(
        id=user_id,
        full_name="Supplier User",
        latitude=-6.175110,  # Different Jakarta coordinates
        longitude=106.865036
    )
    db_session.add(profile)
    db_session.commit()
    
    return user_data

@pytest.fixture
def authenticated_client(client: TestClient, test_user):
    """
    Provide a TestClient that simulates an authenticated user.
    """
    from app.core.dependencies import get_current_user
    from app.main import app
    import uuid
    
    # Create a mock user object with proper UUID
    mock_user = MagicMock()
    mock_user.id = uuid.UUID(test_user["id"])  # Convert string to UUID object
    mock_user.email = test_user["email"]
    
    # Override the get_current_user dependency
    def override_get_current_user():
        return mock_user
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    try:
        yield client
    finally:
        # Clean up the override
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user] 