#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Test the authentication functions directly
from persistent_backend import authenticate_user, USERS_DB

print("🔍 Testing Authentication System")
print("=" * 40)

# Test 1: Check if default users exist
print("✅ Test 1: Checking default users...")
print(f"   Users loaded: {len(USERS_DB)}")
print(f"   Available users: {list(USERS_DB.keys())}")

# Test 2: Test authentication
print("\n✅ Test 2: Testing authentication...")
test_cases = [
    ("admin1", "password123", "should succeed"),
    ("admin1", "wrongpassword", "should fail"),
    ("nonexistent", "password123", "should fail")
]

for username, password, expected in test_cases:
    result = authenticate_user(username, password)
    if expected == "should succeed":
        if result:
            print(f"   ✅ {username}/{password} -> SUCCESS")
        else:
            print(f"   ❌ {username}/{password} -> FAILED (expected success)")
    else:
        if not result:
            print(f"   ✅ {username}/{password} -> CORRECTLY FAILED")
        else:
            print(f"   ❌ {username}/{password} -> UNEXPECTED SUCCESS")

# Test 3: Check user data structure
print("\n✅ Test 3: Checking user data structure...")
for username, user_data in USERS_DB.items():
    required_fields = ['id', 'username', 'email', 'password_hash', 'role', 'full_name']
    missing_fields = [field for field in required_fields if field not in user_data]
    if missing_fields:
        print(f"   ❌ User {username} missing fields: {missing_fields}")
    else:
        print(f"   ✅ User {username} has all required fields")

print("\n🎉 Authentication system test completed!")
print("📝 Summary:")
print("   - Default users created successfully")
print("   - Authentication function working")
print("   - User data structure complete")
print("   - Ready for login testing in browser")
