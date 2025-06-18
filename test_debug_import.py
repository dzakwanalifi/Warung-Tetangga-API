#!/usr/bin/env python3
import requests
import json

def test_import_debug():
    """Test to see the actual import status"""
    try:
        response = requests.get("https://warungwarga-api.azurewebsites.net/info", timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("API Info Response:")
            print(json.dumps(data, indent=2))
            
            # Check the mode
            mode = data.get('mode', 'unknown')
            print(f"\n🔍 Current Mode: {mode}")
            
            # Check endpoints list
            endpoints = data.get('endpoints', [])
            print(f"📋 Total Endpoints: {len(endpoints)}")
            
            router_endpoints = [ep for ep in endpoints if ep.startswith('/auth') or ep.startswith('/users') or ep.startswith('/lapak') or ep.startswith('/borongan') or ep.startswith('/payments')]
            print(f"🔌 Router Endpoints: {len(router_endpoints)}")
            
            for endpoint in router_endpoints:
                print(f"  - {endpoint}")
            
            # Test a specific endpoint to see detailed error
            print(f"\n🧪 Testing a specific endpoint for detailed error:")
            test_response = requests.get("https://warungwarga-api.azurewebsites.net/auth/register", timeout=30)
            print(f"Status: {test_response.status_code}")
            try:
                print(f"Response: {json.dumps(test_response.json(), indent=2)}")
            except:
                print(f"Text Response: {test_response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_import_debug() 