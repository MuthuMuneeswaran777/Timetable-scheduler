import json
import os

print("Checking USERS_DB in persistent backend...")
print("=" * 40)

# Check the current users file
if os.path.exists("users_data.json"):
    with open("users_data.json", "r") as f:
        users_data = json.load(f)

    print("Current users in file:")
    for username, user_data in users_data.items():
        role = user_data["role"]
        password_hash = user_data["password_hash"][:20]
        print(f"  {username}: {role} - Hash: {password_hash}...")

    # Check if persistent_backend can import and load users
    try:
        from persistent_backend import USERS_DB
        print()
        print("USERS_DB loaded by persistent_backend:")
        for username, user_data in USERS_DB.items():
            role = user_data["role"]
            password_hash = user_data["password_hash"][:20]
            print(f"  {username}: {role} - Hash: {password_hash}...")
    except Exception as e:
        print("Error loading USERS_DB:", e)
else:
    print("❌ users_data.json does not exist")
