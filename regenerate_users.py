import json
import os
from persistent_backend import hash_password

print("Regenerating users_data.json with SHA-256 hashes...")
print("=" * 50)

# Default users with SHA-256 hashed passwords
default_users = {
    "admin1": {
        "id": 1,
        "username": "admin1",
        "email": "admin@university.edu",
        "password_hash": hash_password("password123"),
        "role": "admin",
        "full_name": "S.M.Poobalan"
    },
    "faculty1": {
        "id": 2,
        "username": "faculty1",
        "email": "faculty@university.edu",
        "password_hash": hash_password("password123"),
        "role": "faculty",
        "full_name": "Prof. John Smith"
    },
    "student1": {
        "id": 3,
        "username": "student1",
        "email": "student@university.edu",
        "password_hash": hash_password("password123"),
        "role": "student",
        "full_name": "John Doe"
    }
}

# Save to users_data.json
with open("users_data.json", "w") as f:
    json.dump(default_users, f, indent=2)

print("✅ users_data.json regenerated successfully!")
print("Users created:")
for username, user_data in default_users.items():
    print(f"  👤 {username}: {user_data['role']} - Hash: {user_data['password_hash'][:20]}...")

# Test verification
from persistent_backend import verify_password
print()
print("Testing password verification:")
for username, user_data in default_users.items():
    password_hash = user_data["password_hash"]
    verified = verify_password("password123", password_hash)
    print(f"  {username}: {'✅' if verified else '❌'}")
