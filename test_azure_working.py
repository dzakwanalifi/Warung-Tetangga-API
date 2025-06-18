#!/usr/bin/env python3
# test_azure_working.py - Test minimal Azure Functions deployment

import requests
import json
from datetime import datetime

# Azure Functions URL
AZURE_URL = "https://warungwarga-api.azurewebsites.net"

def test_endpoint(name, path, method="GET", data=None):
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
    print(f"🚀 Testing Azure Functions Working Deployment")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL: {AZURE_URL}")
    
    # Test endpoints
    test_endpoint("Root", "/")
    test_endpoint("Health Check", "/health")
    test_endpoint("Test Route", "/test")
    test_endpoint("Info", "/info")
    
    print(f"\n{'='*60}")
    print("✅ Testing completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 