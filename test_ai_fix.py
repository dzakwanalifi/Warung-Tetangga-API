#!/usr/bin/env python3
"""
Test script to validate AI API fixes
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_ai_schema():
    """Test if the AI schema can be imported and has the correct fields"""
    try:
        from app.services.gemini import LapakAnalysisResult
        print("✅ Successfully imported LapakAnalysisResult")
        
        # Check if all required fields are present
        required_fields = ['title', 'description', 'suggested_price', 'unit', 'category']
        schema_fields = list(LapakAnalysisResult.__fields__.keys())
        
        print(f"✅ Schema fields: {schema_fields}")
        
        missing_fields = [field for field in required_fields if field not in schema_fields]
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        print("✅ All required fields are present!")
        
        # Test creating an instance
        test_result = LapakAnalysisResult(
            title="Test Product",
            description="Test description",
            suggested_price=25000,
            unit="kg",
            category="Makanan"
        )
        print(f"✅ Successfully created test instance: {test_result.title}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_router():
    """Test if the API router can be imported"""
    try:
        from app.routers.lapak import router
        print("✅ Successfully imported lapak router")
        
        # Check if analyze endpoint exists
        routes = [route.path for route in router.routes]
        if "/analyze" in routes:
            print("✅ AI analyze endpoint exists in router")
            return True
        else:
            print("❌ AI analyze endpoint not found in router")
            return False
            
    except Exception as e:
        print(f"❌ Error importing router: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing AI API fixes...")
    print("-" * 50)
    
    schema_test = test_ai_schema()
    router_test = test_api_router()
    
    print("-" * 50)
    if schema_test and router_test:
        print("🎉 All tests passed! AI API fixes are working correctly.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1) 