#!/usr/bin/env python3
# test_azure_full.py - Test full Azure Functions deployment with all endpoints

import requests
import json
from datetime import datetime

# Azure Functions URL
AZURE_URL = "https://warungwarga-api.azurewebsites.net"

def test_endpoint(name, path, method="GET", data=None, expected_status=None):
    """Test an endpoint and print results"""
    print(f"\n{'='*60}")
    print(f"Testing {name}: {method} {path}")
    print(f"{'='*60}")
    
    try:
        url = f"{AZURE_URL}{path}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=30)
        else:
            print(f"Method {method} not implemented in test")
            return
        
        print(f"Status Code: {response.status_code}")
        
        # Check if status matches expected
        if expected_status and response.status_code != expected_status:
            print(f"⚠️ Expected {expected_status}, got {response.status_code}")
        elif response.status_code == 200:
            print("✅ Success")
        elif response.status_code in [503, 500]:
            print("⚠️ Service issue (may be database unavailable)")
        elif response.status_code == 404:
            print("🔍 Not Found (endpoint may not exist)")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    print(f"🚀 Testing Full Azure Functions Deployment")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {AZURE_URL}")
    
    # Basic endpoints
    test_endpoint("Root", "/")
    test_endpoint("Health Check", "/health")
    test_endpoint("Database Status", "/db-status")
    test_endpoint("API Info", "/info")
    
    # Authentication endpoints
    print(f"\n{'='*60}")
    print("🔐 AUTHENTICATION ENDPOINTS")
    print(f"{'='*60}")
    test_endpoint("Register", "/auth/register", "POST", {"email": "test@example.com", "password": "test123"})
    test_endpoint("Login", "/auth/login", "POST", {"username": "test@example.com", "password": "test123"})
    
    # Users endpoints
    print(f"\n{'='*60}")
    print("👤 USER ENDPOINTS")
    print(f"{'='*60}")
    test_endpoint("Get User Me", "/users/users/me")
    test_endpoint("Update User Me", "/users/users/me", "PUT", {"name": "Test User"})
    
    # Lapak endpoints
    print(f"\n{'='*60}")
    print("🏪 LAPAK WARGA ENDPOINTS")
    print(f"{'='*60}")
    test_endpoint("Analyze Image", "/lapak/analyze", "POST", {"image_url": "https://example.com/image.jpg"})
    test_endpoint("Create Lapak", "/lapak", "POST", {"title": "Test Lapak", "description": "Test description"})
    test_endpoint("Get Nearby Lapak", "/lapak/nearby")
    test_endpoint("Get Lapak Detail", "/lapak/123")
    test_endpoint("Update Lapak", "/lapak/123", "PUT", {"title": "Updated Lapak"})
    
    # Borongan endpoints
    print(f"\n{'='*60}")
    print("🛒 BORONGAN BARENG ENDPOINTS")
    print(f"{'='*60}")
    test_endpoint("Get Active Borongan", "/borongan/")
    test_endpoint("Create Borongan", "/borongan/", "POST", {"title": "Test Borongan", "description": "Test"})
    test_endpoint("Get Borongan Detail", "/borongan/123")
    test_endpoint("Join Borongan", "/borongan/123/join", "POST", {"quantity": 1})
    
    # Payment endpoints
    print(f"\n{'='*60}")
    print("💳 PAYMENT ENDPOINTS")
    print(f"{'='*60}")
    test_endpoint("Tripay Webhook", "/payments/tripay/webhook", "POST", {"reference": "test123"})
    test_endpoint("Check Payment Status", "/payments/tripay/status/123")
    test_endpoint("Get Payment Methods", "/payments/methods")
    test_endpoint("Get Payment Status", "/payments/status/123")
    
    print(f"\n{'='*60}")
    print("📋 Summary:")
    print("- All endpoints should now be visible in the API")
    print("- Endpoints that require database will return appropriate error messages")
    print("- Check /docs for complete API documentation")
    print("✅ Full testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 