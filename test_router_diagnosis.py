#!/usr/bin/env python3
import requests
import json

BASE_URL = "https://warungwarga-api.azurewebsites.net"

def test_comprehensive_diagnosis():
    """Comprehensive diagnosis of the router issues"""
    
    print("🔍 COMPREHENSIVE ROUTER DIAGNOSIS")
    print("=" * 60)
    
    # 1. Test OpenAPI schema
    print("1️⃣ Testing OpenAPI Schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=30)
        print(f"   OpenAPI Status: {response.status_code}")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get('paths', {})
            print(f"   Paths in OpenAPI: {len(paths)}")
            
            # Count router endpoints in OpenAPI
            router_paths = [path for path in paths.keys() if any(path.startswith(prefix) for prefix in ['/auth', '/users', '/lapak', '/borongan', '/payments'])]
            print(f"   Router paths in OpenAPI: {len(router_paths)}")
            
            if len(router_paths) > 0:
                print("   ✅ Router endpoints present in OpenAPI schema")
                for path in router_paths[:5]:  # Show first 5
                    print(f"      - {path}")
            else:
                print("   ❌ No router endpoints in OpenAPI schema")
    except Exception as e:
        print(f"   ❌ OpenAPI Error: {e}")
    
    print()
    
    # 2. Test specific endpoints with different methods
    print("2️⃣ Testing Specific Endpoints...")
    
    test_cases = [
        ("GET", "/auth/register", "Auth register with GET (should be 405)"),
        ("POST", "/auth/register", "Auth register with POST"),
        ("GET", "/users/users/me", "Users me endpoint"),
        ("GET", "/lapak/nearby", "Lapak nearby endpoint"),
        ("GET", "/borongan/", "Borongan list endpoint"),
    ]
    
    for method, endpoint, description in test_cases:
        print(f"   Testing: {description}")
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", 
                                       json={"test": "data"}, timeout=30)
            
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 405:
                print("      ✅ Method not allowed (endpoint exists)")
            elif response.status_code == 404:
                print("      ❌ Not found (endpoint missing)")
            elif response.status_code == 422:
                print("      ✅ Validation error (endpoint exists)")
            elif response.status_code == 503:
                print("      ✅ Service unavailable (endpoint exists, DB issue)")
            elif response.status_code == 200:
                print("      ✅ Success")
            else:
                print(f"      ⚠️ Unexpected status: {response.status_code}")
                
            # Try to get response details
            try:
                resp_json = response.json()
                if 'detail' in resp_json:
                    print(f"      Detail: {resp_json['detail']}")
            except:
                pass
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        print()
    
    # 3. Test docs page content
    print("3️⃣ Testing Documentation Content...")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=30)
        print(f"   Docs Status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            
            # Check for mock indicators
            if "Mock" in content:
                print("   ❌ Documentation contains 'Mock' text")
                mock_count = content.count("Mock")
                print(f"   Mock occurrences: {mock_count}")
            else:
                print("   ✅ No 'Mock' text found in documentation")
            
            # Check for router endpoints
            router_indicators = ["/auth/register", "/users/users/me", "/lapak/analyze"]
            found_endpoints = [endpoint for endpoint in router_indicators if endpoint in content]
            print(f"   Router endpoints in docs: {len(found_endpoints)}/{len(router_indicators)}")
            
    except Exception as e:
        print(f"   ❌ Docs Error: {e}")
    
    print()
    print("🏁 DIAGNOSIS COMPLETE")

if __name__ == "__main__":
    test_comprehensive_diagnosis() 