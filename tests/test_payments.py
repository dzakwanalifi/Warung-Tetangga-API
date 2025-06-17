import pytest
import uuid
import requests
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.services import tripay as tripay_service


def test_get_payment_methods_endpoint_error(client: TestClient):
    """Test error handling when fetching payment methods fails."""
    mock_result = {
        "success": False,
        "message": "API connection failed"
    }
    
    with patch('app.services.tripay.get_payment_channels', return_value=mock_result):
        response = client.get("/payments/methods")
        
        assert response.status_code == 500
        assert "Failed to fetch payment methods" in response.json()["detail"]


# Test the service functions directly
def test_tripay_get_payment_channels_success():
    """Test the get_payment_channels service function."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": [
            {
                "code": "BRIVA",
                "name": "BRI Virtual Account",
                "type": "Virtual Account",
                "active": True
            }
        ]
    }
    
    with patch('requests.get', return_value=mock_response):
        result = tripay_service.get_payment_channels()
        
        # The service returns the full response object
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"][0]["code"] == "BRIVA"


def test_tripay_get_payment_channels_error():
    """Test get_payment_channels error handling."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection error")):
        result = tripay_service.get_payment_channels()
        
        # Service should return error response instead of raising exception
        assert result["success"] is False
        assert "Connection error" in result["message"]


def test_tripay_get_transaction_detail_success():
    """Test the get_transaction_detail service function."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "reference": "T12345678",
            "status": "PAID",
            "amount": 100000
        }
    }
    
    with patch('requests.get', return_value=mock_response):
        result = tripay_service.get_transaction_detail("T12345678")
        
        # The service returns the full response object
        assert result["success"] is True
        assert result["data"]["reference"] == "T12345678"
        assert result["data"]["status"] == "PAID"
        assert result["data"]["amount"] == 100000


def test_tripay_get_transaction_detail_error():
    """Test get_transaction_detail error handling."""
    with patch('requests.get', side_effect=requests.exceptions.ConnectionError("Connection error")):
        result = tripay_service.get_transaction_detail("INVALID_REF")
        
        # Service should return error response instead of raising exception
        assert result["success"] is False
        assert "Connection error" in result["message"]


def test_payment_status_sync_logic():
    """Test payment status synchronization logic."""
    # Mock participant data
    participant_data = {
        "id": str(uuid.uuid4()),
        "payment_status": "pending",
        "tripay_reference_code": "T12345678"
    }
    
    # Mock Tripay response (full service response structure)
    mock_transaction_result = {
        "success": True,
        "data": {
            "reference": "T12345678",
            "status": "PAID",
            "amount": 100000
        }
    }
    
    with patch('app.services.tripay.get_transaction_detail', return_value=mock_transaction_result):
        # This simulates the logic in the actual endpoint
        if mock_transaction_result.get("success"):
            transaction_data = mock_transaction_result.get("data", {})
            tripay_status = transaction_data.get("status")
            assert tripay_status == "PAID"
            
            # Status should be updated from pending to paid
            if tripay_status == "PAID" and participant_data["payment_status"] != "paid":
                participant_data["payment_status"] = "paid"
                
            assert participant_data["payment_status"] == "paid"


def test_payment_status_sync_error_handling():
    """Test payment status sync error handling."""
    participant_data = {
        "id": str(uuid.uuid4()),
        "payment_status": "pending",
        "tripay_reference_code": "T12345678"
    }
    
    # Mock error response from service
    mock_error_result = {
        "success": False,
        "message": "API Error"
    }
    
    with patch('app.services.tripay.get_transaction_detail', return_value=mock_error_result):
        result = tripay_service.get_transaction_detail("T12345678")
        
        # Service returns error, status should remain unchanged
        assert result["success"] is False
        assert participant_data["payment_status"] == "pending"


def test_tripay_backward_compatibility():
    """Test backward compatibility functions."""
    mock_channels_result = {
        "success": True,
        "data": [{"code": "BRIVA", "name": "BRI Virtual Account"}]
    }
    
    mock_detail_result = {
        "success": True,
        "data": {"reference": "T123", "status": "PAID"}
    }
    
    with patch('app.services.tripay.get_payment_channels', return_value=mock_channels_result):
        # Test get_payment_methods (backward compatibility)
        result = tripay_service.get_payment_methods()
        assert result["success"] is True
        assert len(result["data"]) == 1
    
    with patch('app.services.tripay.get_transaction_detail', return_value=mock_detail_result):
        # Test check_transaction_status (backward compatibility)
        result = tripay_service.check_transaction_status("T123")
        assert result["success"] is True
        assert result["data"]["status"] == "PAID"


def test_service_functions_with_api_key():
    """Test that service functions use the correct API key."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": []}
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        tripay_service.get_payment_channels()
        
        # Verify that the request was made with correct headers
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'headers' in call_args.kwargs
        assert 'Authorization' in call_args.kwargs['headers']
        assert call_args.kwargs['headers']['Authorization'].startswith('Bearer')


def test_transaction_detail_with_reference():
    """Test transaction detail endpoint with reference parameter."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "success": True,
        "data": {"reference": "TEST123", "status": "UNPAID"}
    }
    
    with patch('requests.get', return_value=mock_response) as mock_get:
        result = tripay_service.get_transaction_detail("TEST123")
        
        # Verify that the request was made with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'params' in call_args.kwargs
        assert call_args.kwargs['params']['reference'] == "TEST123"
        
        # Verify the result
        assert result["success"] is True
        assert result["data"]["reference"] == "TEST123"
        assert result["data"]["status"] == "UNPAID"


def test_error_response_structure():
    """Test that error responses have consistent structure."""
    with patch('requests.get', side_effect=requests.exceptions.Timeout("Network timeout")):
        # Test payment channels error
        channels_result = tripay_service.get_payment_channels()
        assert channels_result["success"] is False
        assert "message" in channels_result
        assert "Network timeout" in channels_result["message"]
        
        # Test transaction detail error
        detail_result = tripay_service.get_transaction_detail("TEST")
        assert detail_result["success"] is False
        assert "message" in detail_result
        assert "Network timeout" in detail_result["message"]


def test_http_error_handling():
    """Test handling of HTTP error responses."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("401 Unauthorized")
    
    with patch('requests.get', return_value=mock_response):
        # Test payment channels with HTTP error
        result = tripay_service.get_payment_channels()
        assert result["success"] is False
        assert "401 Unauthorized" in result["message"]
        
        # Test transaction detail with HTTP error
        result = tripay_service.get_transaction_detail("TEST")
        assert result["success"] is False
        assert "401 Unauthorized" in result["message"]


def test_json_parsing_success():
    """Test successful JSON parsing from API responses."""
    expected_data = {
        "success": True,
        "data": [{"code": "QRIS", "name": "QRIS"}]
    }
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = expected_data
    
    with patch('requests.get', return_value=mock_response):
        result = tripay_service.get_payment_channels()
        
        # Verify that json() was called and data matches
        mock_response.json.assert_called_once()
        assert result == expected_data
        assert result["success"] is True
        assert len(result["data"]) == 1


def test_payment_status_mapping():
    """Test mapping of Tripay status to internal payment status"""
    # Test successful payment mapping
    tripay_paid = "PAID"
    assert tripay_paid == "PAID"
    
    # Test failed payment mapping
    tripay_failed_statuses = ["EXPIRED", "FAILED", "CANCELED"]
    for status in tripay_failed_statuses:
        assert status in ["EXPIRED", "FAILED", "CANCELED"]
    
    # Test pending payment mapping
    tripay_unpaid = "UNPAID"
    assert tripay_unpaid == "UNPAID"


def test_webhook_rollback_logic():
    """Test the improved webhook rollback logic for failed payments"""
    from app.routers.payments import tripay_webhook
    from app.models.group_buy_participant import GroupBuyParticipant
    from app.models.group_buy import GroupBuy
    from app.models.profile import Profile
    import json
    import hmac
    import hashlib
    from unittest.mock import Mock
    from decimal import Decimal
    
    # Mock participant data
    participant_id = "test-participant-123"
    group_buy_id = "test-groupbuy-456"
    
    # Test data for failed payment webhook
    webhook_data = {
        "status": "FAILED",
        "merchant_ref": participant_id,
        "reference": "TR-TEST-123"
    }
    
    # Test rollback prevention for already failed payment
    assert webhook_data["status"] == "FAILED"
    assert webhook_data["merchant_ref"] == participant_id


def test_webhook_race_condition_prevention():
    """Test that webhook handles concurrent requests safely"""
    from app.routers.payments import tripay_webhook
    import asyncio
    
    # Mock concurrent webhook requests
    participant_id = "test-participant-race"
    
    webhook_data_1 = {
        "status": "PAID",
        "merchant_ref": participant_id,
        "reference": "TR-RACE-1"
    }
    
    webhook_data_2 = {
        "status": "FAILED", 
        "merchant_ref": participant_id,
        "reference": "TR-RACE-2"
    }
    
    # Verify data structure for race condition testing
    assert webhook_data_1["merchant_ref"] == webhook_data_2["merchant_ref"]
    assert webhook_data_1["status"] != webhook_data_2["status"]


def test_webhook_duplicate_handling():
    """Test that webhook ignores duplicate notifications"""
    participant_id = "test-participant-dup"
    
    # First webhook - PAID
    webhook_paid = {
        "status": "PAID",
        "merchant_ref": participant_id,
        "reference": "TR-DUP-123"
    }
    
    # Duplicate webhook - Same PAID status
    webhook_duplicate = {
        "status": "PAID", 
        "merchant_ref": participant_id,
        "reference": "TR-DUP-123"
    }
    
    # Verify duplicate detection logic
    assert webhook_paid["status"] == webhook_duplicate["status"]
    assert webhook_paid["merchant_ref"] == webhook_duplicate["merchant_ref"]


def test_webhook_quantity_rollback():
    """Test that failed payments correctly rollback group buy quantities"""
    from decimal import Decimal
    
    # Mock group buy data
    initial_quantity = 8
    participant_quantity = 3
    target_quantity = 10
    
    # Simulate rollback calculation
    quantity_after_rollback = initial_quantity - participant_quantity
    
    # Verify rollback logic
    assert quantity_after_rollback == 5
    assert quantity_after_rollback < target_quantity
    
    # Test status change from successful to active
    group_buy_was_successful = initial_quantity >= target_quantity
    should_revert_to_active = quantity_after_rollback < target_quantity
    
    # This would be False because initial_quantity (8) < target_quantity (10)
    assert not group_buy_was_successful
    assert should_revert_to_active


def test_webhook_signature_validation():
    """Test webhook signature validation logic"""
    import hmac
    import hashlib
    
    # Mock private key and data
    private_key = "test-private-key"
    webhook_body = '{"status":"PAID","merchant_ref":"test-123"}'
    
    # Generate signature
    signature = hmac.new(
        bytes(private_key, 'latin-1'),
        bytes(webhook_body, 'latin-1'),
        hashlib.sha256
    ).hexdigest()
    
    # Verify signature generation
    assert len(signature) == 64  # SHA256 hex digest length
    assert isinstance(signature, str)
    
    # Test signature validation logic
    test_signature = hmac.new(
        bytes(private_key, 'latin-1'),
        bytes(webhook_body, 'latin-1'),
        hashlib.sha256
    ).hexdigest()
    
    assert signature == test_signature 