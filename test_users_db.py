import json
import os

print("Testing USERS_DB directly...")
print("=" * 30)

# Check if users file exists
if os.path.exists("users_data.json"):
    print("✅ users_data.json exists")
    with open("users_data.json", "r") as f:
        users_db = json.load(f)

    print("Users in database:")
    for username, user_data in users_db.items():
        role = user_data.get("role", "N/A")
        print(f"  {username}: {role}")

    # Test password verification
    try:
        import sys
        sys.path.append(".")
        from persistent_backend import verify_password

        admin_user = users_db.get("admin1")
        if admin_user:
            password_hash = admin_user["password_hash"]
            print("Admin password hash:", password_hash)
            print("Password verification test:")
            print("  password123:", verify_password("password123", password_hash))
            print("  wrongpass:", verify_password("wrongpass", password_hash))
    except Exception as e:
        print("Error testing password verification:", e)
else:
    print("❌ users_data.json does not exist")
