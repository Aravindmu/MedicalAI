import requests
import json
import time

print("\n" + "=" * 60)
print("TESTING MEDIPULSE AI ENDPOINTS")
print("=" * 60)

# Test 1: Chat API
print("\n[TEST 1] Chat API Endpoint")
print("-" * 60)

try:
    response = requests.post(
        "http://localhost:5000/api/chat",
        json={"message": "What are the signs of good health?"},
        timeout=60
    )
    print(f"✅ Status Code: {response.status_code}")
    result = response.json()
    if 'reply' in result:
        print(f"✅ Response received:")
        print(f"   {result['reply'][:200]}...")
    else:
        print(f"❌ Response: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)

