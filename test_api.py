#!/usr/bin/env python3
"""
Simple test script for Warung Warga API production deployment
"""

import requests
import json
from datetime import datetime

AZURE_URL = "https://warungwarga-api.azurewebsites.net"

def test_api():
    """Test basic API functionality"""
    
    print(f"🚀 Testing Warung Warga API")
    print(f"🌐 URL: {AZURE_URL}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test basic endpoints
    endpoints = [
        ("Root", "/"),
        ("Health Check", "/health"),
        ("Database Status", "/db-status"),
        ("API Info", "/info")
    ]
    
    for name, path in endpoints:
        print(f"\n📍 Testing {name}: {path}")
        try:
            response = requests.get(f"{AZURE_URL}{path}", timeout=30)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ Success")
            elif response.status_code == 503:
                print("   ⚠️ Service Unavailable (Database not connected)")
            else:
                print(f"   ❌ Error: {response.status_code}")
                
            # Show response preview
            try:
                data = response.json()
                if 'message' in data:
                    print(f"   📝 Message: {data['message']}")
                if 'mode' in data:
                    print(f"   🔧 Mode: {data['mode']}")
            except:
                pass
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ API testing completed!")
    print(f"📖 Documentation: {AZURE_URL}/docs")

if __name__ == "__main__":
    test_api() 