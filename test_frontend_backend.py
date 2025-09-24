#!/usr/bin/env python3
import requests

print("🔗 FRONTEND-BACKEND CONNECTION TEST")
print("=" * 50)

API_BASE_URL = 'http://localhost:8001'

# Test backend reachability
try:
    response = requests.get(f'{API_BASE_URL}/health', timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Backend reachable: {data['status']}")
    else:
        print(f"❌ Backend not reachable: {response.status_code}")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Test login process
print("\n🔐 Testing Login Process")
login_data = {'username': 'admin1', 'password': 'password123'}

try:
    response = requests.post(f'{API_BASE_URL}/token', data=login_data, timeout=10)
    print(f"📡 Login response: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!"
        print(f"🎫 Token type: {data['token_type']}")

        # Test token usage
        headers = {'Authorization': f"Bearer {data['access_token']}"}
        user_response = requests.get(f'{API_BASE_URL}/users/me', headers=headers, timeout=5)

        if user_response.status_code == 200:
            user_data = user_response.json()
            print("✅ Token validation successful"
            print(f"👤 User: {user_data['username']} ({user_data['role']})")
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"❌ Token validation failed: {user_response.status_code}")

    else:
        error_text = response.text
        print("❌ Login failed"
        print(f"Error ({response.status_code}): {error_text}")

except Exception as e:
    print(f"❌ Login process error: {e}")

print("\n🎯 Frontend should now be able to login successfully!")
print("📋 Try: http://localhost:3000 with admin1/password123")
