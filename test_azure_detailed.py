#!/usr/bin/env python3
"""
Detailed test script untuk debugging Azure Function App
"""

import requests
import json
from datetime import datetime

def test_azure_function_detailed():
    """Test dengan berbagai URL pattern untuk debugging"""
    
    base_url = "https://warungwarga-api.azurewebsites.net"
    
    print(f"🔍 Detailed Testing Azure Function App")
    print(f"🌐 Base URL: {base_url}")
    print(f"⏰ Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Test berbagai URL pattern
    test_urls = [
        "/",
        "/api/HttpTrigger",  # Default Azure Functions pattern
        "/HttpTrigger",      # Without /api prefix
        "/health",           # FastAPI endpoint
        "/docs",             # FastAPI docs
        "/api/health",       # With /api prefix
        "/api/docs",         # With /api prefix
        "/api/products",     # Products endpoint
    ]
    
    for i, url_path in enumerate(test_urls, 1):
        print(f"{i}️⃣ Testing: {url_path}")
        try:
            full_url = f"{base_url}{url_path}"
            response = requests.get(full_url, timeout=30)
            print(f"   ✅ Status: {response.status_code}")
            
            # Show response content for 200 responses
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'N/A')
                print(f"   📄 Content-Type: {content_type}")
                
                if 'json' in content_type.lower():
                    try:
                        json_data = response.json()
                        print(f"   📝 JSON Response: {json.dumps(json_data, indent=2)[:200]}...")
                    except:
                        print(f"   📝 Response (first 200 chars): {response.text[:200]}")
                else:
                    print(f"   📝 Response (first 200 chars): {response.text[:200]}")
            else:
                print(f"   ❌ Error Response: {response.text[:100]}")
                
        except Exception as e:
            print(f"   💥 Exception: {str(e)}")
        
        print()

if __name__ == "__main__":
    test_azure_function_detailed() 