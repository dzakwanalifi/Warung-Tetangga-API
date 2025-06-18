#!/usr/bin/env python3
"""
Test script untuk menguji deployment Azure Function App
"""

import requests
import json
from datetime import datetime

def test_function_app():
    """Test basic functionality of the deployed function app"""
    
    base_url = "https://warungwarga-api.azurewebsites.net"
    
    print(f"🔄 Testing Azure Function App at: {base_url}")
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Test 1: Root endpoint
    try:
        print("1️⃣ Testing root endpoint...")
        response = requests.get(f"{base_url}/", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print()
    
    # Test 2: Health check
    try:
        print("2️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print()
    
    # Test 3: API docs
    try:
        print("3️⃣ Testing API docs endpoint...")
        response = requests.get(f"{base_url}/docs", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Content Type: {response.headers.get('content-type', 'N/A')}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print()
    
    # Test 4: Products endpoint
    try:
        print("4️⃣ Testing products endpoint...")
        response = requests.get(f"{base_url}/api/products", timeout=30)
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        print()

if __name__ == "__main__":
    test_function_app() 