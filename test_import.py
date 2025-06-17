#!/usr/bin/env python3
import sys
import traceback

print("Testing import of api.app.main...")

try:
    import api.app.main
    print("✅ SUCCESS: api.app.main imported successfully")
    print(f"App object: {type(api.app.main.app)}")
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()

print(f"\nPython version: {sys.version}")
print(f"Python path: {sys.path}") 