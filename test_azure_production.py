#!/usr/bin/env python3
# test_azure_production.py - Test production Azure Functions deployment

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
            print("⚠️ Service issue (expected during startup)")
        
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def main():
    print(f"🚀 Testing Azure Functions Production Deployment")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {AZURE_URL}")
    
    # Basic endpoints
    test_endpoint("Root", "/")
    test_endpoint("Health Check", "/health")
    test_endpoint("Database Status", "/db-status")
    test_endpoint("API Info", "/info")
    
    # Try some API endpoints (these might fail if database is not available)
    test_endpoint("Auth Endpoints", "/auth/test", expected_status=404)  # Might not exist
    test_endpoint("Users Endpoints", "/users", expected_status=404)   # Might not exist
    
    print(f"\n{'='*60}")
    print("📋 Summary:")
    print("- If database is available, all endpoints should work")
    print("- If database is not available, basic endpoints should still work")
    print("- Check /db-status for database connection info")
    print("✅ Testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 