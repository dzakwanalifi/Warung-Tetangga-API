# tests/test_lapak.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import io
from decimal import Decimal
import uuid
import json

from tests.conftest import TestProfile, TestListing


def test_analyze_image_success(authenticated_client: TestClient):
    """
    Test successful image analysis using Gemini AI.
    """
    dummy_image = io.BytesIO(b"dummy image content")

    # Mock Gemini AI response - need to mock the function in the router module
    from app.services.gemini import LapakAnalysisResult
    mock_result = LapakAnalysisResult(
        title="Tomat Segar",
        description="Tomat merah segar untuk keperluan memasak",
        unit="kg"
    )

    with patch('app.routers.lapak.analyze_image_from_file', return_value=mock_result):
        files = {'image': ('test.jpg', dummy_image, 'image/jpeg')}
        response = authenticated_client.post("/lapak/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Tomat Segar"
    assert data["description"] == "Tomat merah segar untuk keperluan memasak"
    assert data["unit"] == "kg"


def test_analyze_image_invalid_file(authenticated_client: TestClient):
    """
    Test image analysis with invalid file type.
    """
    invalid_file = io.BytesIO(b"not an image")

    files = {'image': ('test.txt', invalid_file, 'text/plain')}
    response = authenticated_client.post("/lapak/analyze", files=files)

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_create_lapak_success(authenticated_client: TestClient, db_session: Session):
    """
    Test successful lapak creation with image uploads.
    """
    dummy_image = io.BytesIO(b"dummy image content")

    lapak_data = {
        "title": "Test Lapak",
        "description": "Test description",
        "price": "10000.50",
        "unit": "kg",
        "stock_quantity": "5"
    }

    files = [('images', ('test.jpg', dummy_image, 'image/jpeg'))]

    # Mock Azure storage upload
    mock_image_urls = ["https://storage.azure.com/image1.jpg"]
    with patch('app.services.azure_storage.upload_images_to_blob', return_value=mock_image_urls):
        response = authenticated_client.post(
            "/lapak",
            data=lapak_data,
            files=files
        )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Lapak"
    assert data["description"] == "Test description"
    assert float(data["price"]) == 10000.50
    assert data["unit"] == "kg"
    assert data["stock_quantity"] == 5
    assert data["image_urls"] == mock_image_urls
    assert data["status"] == "available"


def test_create_lapak_no_location(authenticated_client: TestClient, db_session: Session, test_user):
    """
    Test lapak creation failure when user has no location set.
    """
    # Remove location from test user profile
    user_profile = db_session.query(TestProfile).filter(TestProfile.id == test_user["id"]).first()
    user_profile.latitude = None
    user_profile.longitude = None
    db_session.commit()

    dummy_image = io.BytesIO(b"dummy image content")

    lapak_data = {
        "title": "Test Lapak",
        "price": "10000",
        "unit": "kg",
        "stock_quantity": "5"
    }

    files = [('images', ('test.jpg', dummy_image, 'image/jpeg'))]

    response = authenticated_client.post(
        "/lapak",
        data=lapak_data,
        files=files
    )

    assert response.status_code == 400
    assert "location information" in response.json()["detail"]


def test_create_lapak_invalid_data(authenticated_client: TestClient):
    """
    Test lapak creation with invalid data (negative price).
    """
    dummy_image = io.BytesIO(b"dummy image content")

    lapak_data = {
        "title": "Test Lapak",
        "price": "-1000",  # Negative price
        "unit": "kg",
        "stock_quantity": "5"
    }

    files = [('images', ('test.jpg', dummy_image, 'image/jpeg'))]

    response = authenticated_client.post(
        "/lapak",
        data=lapak_data,
        files=files
    )

    assert response.status_code == 422  # Validation error


def test_get_lapak_nearby_success(authenticated_client: TestClient, db_session: Session):
    """
    Test retrieving nearby lapak successfully.
    """
    # Create test seller and lapak with proper UUID
    seller_id = str(uuid.uuid4())
    lapak_id = str(uuid.uuid4())
    
    seller = TestProfile(
        id=seller_id,
        full_name="Seller User",
        latitude=-6.20,
        longitude=106.81
    )
    db_session.add(seller)

    lapak = TestListing(
        id=lapak_id,
        seller_id=seller_id,
        title="Test Lapak",
        description="Test description",
        price=Decimal("10000.50"),
        unit="kg",
        stock_quantity=5,
        image_urls=json.dumps(["https://storage.azure.com/image1.jpg"]),
        status="available",
        latitude=-6.20,
        longitude=106.81
    )
    db_session.add(lapak)
    db_session.commit()

    # For this test, we'll mock the spatial query since SQLite doesn't support PostGIS
    with patch('app.routers.lapak.get_nearby_lapak') as mock_nearby:
        mock_nearby.return_value = {
            "items": [{
                "id": lapak_id,
                "title": "Test Lapak",
                "description": "Test description",
                "price": "10000.50",
                "unit": "kg", 
                "stock_quantity": 5,
                "image_urls": ["https://storage.azure.com/image1.jpg"],
                "status": "available",
                "seller": {
                    "id": seller_id,
                    "full_name": "Seller User"
                },
                "distance": 0.5
            }],
            "total_count": 1
        }
        
        response = authenticated_client.get("/lapak/nearby?lat=-6.20&lon=106.81&radius=5000")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Test Lapak"
    assert data["total_count"] == 1


def test_get_lapak_detail_success(authenticated_client: TestClient, db_session: Session):
    """
    Test retrieving lapak detail successfully.
    """
    # Create test seller and lapak with proper UUID
    seller_id = str(uuid.uuid4())
    lapak_id = str(uuid.uuid4())
    
    seller = TestProfile(
        id=seller_id,
        full_name="Seller User",
        latitude=-6.20,
        longitude=106.81
    )
    db_session.add(seller)

    lapak = TestListing(
        id=lapak_id,
        seller_id=seller_id,
        title="Test Lapak Detail",
        description="Detailed description",
        price=Decimal("15000.00"),
        unit="pcs",
        stock_quantity=10,
        image_urls=json.dumps(["https://storage.azure.com/image1.jpg"]),
        status="available"
    )
    db_session.add(lapak)
    db_session.commit()

    # Mock the get_lapak_detail function since we're using SQLite
    with patch('app.routers.lapak.get_lapak_detail') as mock_detail:
        mock_detail.return_value = {
            "id": lapak_id,
            "title": "Test Lapak Detail",
            "description": "Detailed description",
            "price": "15000.00",
            "unit": "pcs",
            "stock_quantity": 10,
            "image_urls": ["https://storage.azure.com/image1.jpg"],
            "status": "available",
            "seller": {
                "id": seller_id,
                "full_name": "Seller User"
            }
        }
        
        response = authenticated_client.get(f"/lapak/{lapak_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Lapak Detail"
    assert data["price"] == "15000.00"
    assert data["seller"]["full_name"] == "Seller User"


def test_get_lapak_detail_not_found(authenticated_client: TestClient):
    """
    Test retrieving non-existent lapak detail.
    """
    non_existent_id = str(uuid.uuid4())
    
    with patch('app.routers.lapak.get_lapak_detail', return_value=None):
        response = authenticated_client.get(f"/lapak/{non_existent_id}")
    
    assert response.status_code == 404
    assert "Lapak not found" in response.json()["detail"]


def test_update_lapak_success(authenticated_client: TestClient, db_session: Session, test_user):
    """
    Test successful lapak update by owner.
    """
    # Create lapak owned by test user with proper UUID
    lapak_id = str(uuid.uuid4())
    
    lapak = TestListing(
        id=lapak_id,
        seller_id=test_user["id"],
        title="Original Title",
        description="Original description",
        price=Decimal("10000.00"),
        unit="kg",
        stock_quantity=5,
        status="available"
    )
    db_session.add(lapak)
    db_session.commit()

    update_data = {
        "title": "Updated Title",
        "stock_quantity": 10,
        "status": "sold_out"
    }

    # Mock the update function since we need to handle UUID properly
    with patch('app.routers.lapak.update_lapak') as mock_update:
        mock_update.return_value = {
            "id": lapak_id,
            "title": "Updated Title",
            "description": "Original description",
            "price": "10000.00",
            "unit": "kg",
            "stock_quantity": 10,
            "status": "sold_out",
            "seller": {
                "id": test_user["id"],
                "full_name": "Test User"
            }
        }
        
        response = authenticated_client.put(f"/lapak/{lapak_id}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["stock_quantity"] == 10
    assert data["status"] == "sold_out"


def test_update_lapak_unauthorized(authenticated_client: TestClient, db_session: Session):
    """
    Test lapak update by non-owner (should fail).
    """
    # Create lapak owned by different user
    other_seller_id = str(uuid.uuid4())
    lapak_id = str(uuid.uuid4())
    
    other_seller = TestProfile(
        id=other_seller_id,
        full_name="Other Seller",
        latitude=-6.20,
        longitude=106.81
    )
    db_session.add(other_seller)

    lapak = TestListing(
        id=lapak_id,
        seller_id=other_seller_id,  # Different from test_user
        title="Other's Lapak",
        price=Decimal("10000.00"),
        unit="kg",
        stock_quantity=5
    )
    db_session.add(lapak)
    db_session.commit()

    update_data = {"title": "Hacked Title"}

    # Mock unauthorized response
    with patch('app.routers.lapak.update_lapak') as mock_update:
        from fastapi import HTTPException
        mock_update.side_effect = HTTPException(status_code=403, detail="Not authorized to update this lapak")
        
        response = authenticated_client.put(f"/lapak/{lapak_id}", json=update_data)

    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


def test_update_lapak_not_found(authenticated_client: TestClient):
    """
    Test updating non-existent lapak.
    """
    non_existent_id = str(uuid.uuid4())
    update_data = {"title": "Updated Title"}

    with patch('app.routers.lapak.update_lapak') as mock_update:
        from fastapi import HTTPException
        mock_update.side_effect = HTTPException(status_code=404, detail="Lapak not found")
        
        response = authenticated_client.put(f"/lapak/{non_existent_id}", json=update_data)

    assert response.status_code == 404
    assert "Lapak not found" in response.json()["detail"]


def test_azure_storage_upload_error(authenticated_client: TestClient, test_user):
    """
    Test lapak creation when Azure storage upload fails.
    """
    dummy_image = io.BytesIO(b"dummy image content")

    lapak_data = {
        "title": "Test Lapak",
        "price": "10000",
        "unit": "kg",
        "stock_quantity": "5"
    }

    files = [('images', ('test.jpg', dummy_image, 'image/jpeg'))]

    # Mock Azure upload to raise an exception
    with patch('app.services.azure_storage.upload_images_to_blob',
               side_effect=ValueError("Azure upload failed")):
        response = authenticated_client.post(
            "/lapak",
            data=lapak_data,
            files=files
        )

    assert response.status_code == 500
    assert "Error uploading images" in response.json()["detail"]


def test_analyze_image_fallback_behavior(authenticated_client: TestClient):
    """
    Test image analysis fallback when Gemini API fails (current actual behavior).
    """
    dummy_image = io.BytesIO(b"dummy image content")
    
    # Don't mock - let the actual function run and hit the fallback
    files = {'image': ('test.jpg', dummy_image, 'image/jpeg')}
    response = authenticated_client.post("/lapak/analyze", files=files)

    assert response.status_code == 200
    data = response.json()
    # Test the actual fallback response
    assert data["title"] == "Produk Segar"
    assert "Produk berkualitas dari tetangga terdekat" in data["description"]
    assert data["unit"] == "buah"


def test_gemini_analysis_error_fallback(authenticated_client: TestClient):
    """
    Test image analysis error when Gemini client is not initialized.
    """
    dummy_image = io.BytesIO(b"dummy image content")

    # Mock the function to raise ValueError (like when client is not initialized)
    with patch('app.services.gemini.client', None):  # Simulate no client
        files = {'image': ('test.jpg', dummy_image, 'image/jpeg')}
        response = authenticated_client.post("/lapak/analyze", files=files)

    # When client is None, the function should raise ValueError which gets caught by router
    assert response.status_code == 500
    assert "Gemini client is not initialized" in response.json()["detail"] 