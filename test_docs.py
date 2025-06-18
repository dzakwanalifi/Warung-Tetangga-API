#!/usr/bin/env python3
import requests

def test_docs():
    try:
        response = requests.get("https://warungwarga-api.azurewebsites.net/docs", timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Docs endpoint is accessible")
            # Check if it contains typical FastAPI docs content
            if "FastAPI" in response.text or "swagger" in response.text.lower():
                print("✅ Contains FastAPI documentation")
            else:
                print("⚠️ May not contain proper FastAPI docs")
        else:
            print(f"❌ Docs endpoint returned {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing docs: {e}")

if __name__ == "__main__":
    test_docs() 