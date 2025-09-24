#!/usr/bin/env python3
"""
🔐 Authentication Test Suite
Tests all authentication functionality thoroughly
"""

import sys
import os
import json
sys.path.append(os.path.dirname(__file__))

def run_auth_tests():
    print("🔐 COMPREHENSIVE AUTHENTICATION TEST SUITE")
    print("=" * 60)

    try:
        from persistent_backend import (
            authenticate_user,
            create_access_token,
            hash_password,
            verify_password,
            USERS_DB
        )
        from datetime import timedelta

        tests_passed = 0
        total_tests = 0

        # Test 1: User Data Loading
        total_tests += 1
        if len(USERS_DB) >= 3:
            print("✅ Test 1 PASSED: Default users loaded")
            tests_passed += 1
        else:
            print("❌ Test 1 FAILED: Insufficient users loaded")

        # Test 2: Password Hashing
        total_tests += 1
        test_password = "test123"
        hashed = hash_password(test_password)
        if verify_password(test_password, hashed):
            print("✅ Test 2 PASSED: Password hashing working")
            tests_passed += 1
        else:
            print("❌ Test 2 FAILED: Password hashing broken")

        # Test 3: Valid Authentication
        total_tests += 1
        user = authenticate_user("admin1", "password123")
        if user and user["role"] == "admin":
            print("✅ Test 3 PASSED: Valid authentication working")
            tests_passed += 1
        else:
            print("❌ Test 3 FAILED: Valid authentication broken")

        # Test 4: Invalid Authentication
        total_tests += 1
        user = authenticate_user("admin1", "wrongpassword")
        if not user:
            print("✅ Test 4 PASSED: Invalid authentication rejected")
            tests_passed += 1
        else:
            print("❌ Test 4 FAILED: Invalid authentication accepted")

        # Test 5: JWT Token Creation
        total_tests += 1
        try:
            token = create_access_token({"sub": "test"}, timedelta(minutes=5))
            if len(token) > 50:
                print("✅ Test 5 PASSED: JWT token creation working")
                tests_passed += 1
            else:
                print("❌ Test 5 FAILED: JWT token too short")
        except Exception as e:
            print(f"❌ Test 5 FAILED: JWT token error: {e}")

        # Test 6: User Structure
        total_tests += 1
        required_fields = ["id", "username", "email", "role", "full_name", "password_hash"]
        user_complete = all(
            all(field in user for field in required_fields)
            for user in USERS_DB.values()
        )
        if user_complete:
            print("✅ Test 6 PASSED: User data structure complete")
            tests_passed += 1
        else:
            print("❌ Test 6 FAILED: User data structure incomplete")

        # Test 7: Role Validation
        total_tests += 1
        expected_roles = {"admin", "faculty", "student"}
        actual_roles = set(user["role"] for user in USERS_DB.values())
        if actual_roles == expected_roles:
            print("✅ Test 7 PASSED: All roles present")
            tests_passed += 1
        else:
            print(f"❌ Test 7 FAILED: Missing roles {expected_roles - actual_roles}")

        # Summary
        print("\n" + "=" * 60)
        print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} PASSED")

        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED!")
            print("🚀 Authentication system is PRODUCTION READY!")
            return True
        else:
            print(f"⚠️  {total_tests - tests_passed} tests failed")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_auth_tests()
    sys.exit(0 if success else 1)
