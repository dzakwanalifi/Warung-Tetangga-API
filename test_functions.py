#!/usr/bin/env python3
"""
Test script to verify all Azure Functions can be imported correctly
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def test_function_imports():
    """Test importing all function apps"""
    print("🔍 Testing Azure Function imports...")
    
    functions_to_test = [
        ("AuthFunction", "app_auth"),
        ("BoronganFunction", "app_borongan"), 
        ("LapakFunction", "app_lapak"),
        ("PaymentsFunction", "app_payments"),
        ("UsersFunction", "app_users")
    ]
    
    results = []
    
    for function_name, app_name in functions_to_test:
        try:
            module = __import__(f"{function_name}.__init__", fromlist=[app_name])
            app = getattr(module, app_name)
            print(f"✅ {function_name}: {app_name} imported successfully")
            
            # Test that it's a FastAPI app
            if hasattr(app, 'routes'):
                route_count = len(app.routes)
                print(f"   📍 {route_count} routes registered")
            
            results.append((function_name, True, None))
            
        except Exception as e:
            print(f"❌ {function_name}: Failed to import - {str(e)}")
            results.append((function_name, False, str(e)))
    
    print("\n📊 Summary:")
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"✅ Successful imports: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 All Azure Functions are ready for deployment!")
        return True
    else:
        print("⚠️  Some functions need attention before deployment")
        return False

if __name__ == "__main__":
    test_function_imports() 