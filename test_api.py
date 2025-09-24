#!/usr/bin/env python3
"""
Test the API endpoints
"""

import requests
import json

def test_api():
    """Test the rooms API endpoint"""
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        print("Testing health endpoint...")
        response = requests.get(f"{base_url}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test rooms list endpoint
        print("\nTesting rooms list endpoint...")
        response = requests.get(f"{base_url}/data/rooms")
        print(f"Rooms list: {response.status_code}")
        if response.status_code == 200:
            rooms = response.json()
            print(f"Found {len(rooms)} rooms: {rooms}")
        else:
            print(f"Error: {response.text}")
        
        # Test creating a room
        print("\nTesting room creation...")
        room_data = {
            "room_name": "Test Room 101",
            "capacity": 30,
            "room_type": "CLASSROOM",
            "assigned_batch_id": None
        }
        response = requests.post(f"{base_url}/data/rooms", json=room_data)
        print(f"Create room: {response.status_code}")
        if response.status_code == 200:
            created_room = response.json()
            print(f"Created room: {created_room}")
            
            # Clean up - delete the test room
            room_id = created_room.get("room_id")
            if room_id:
                delete_response = requests.delete(f"{base_url}/data/rooms/{room_id}")
                print(f"Deleted test room: {delete_response.status_code}")
        else:
            print(f"Error creating room: {response.text}")
            
    except Exception as e:
        print(f"API test failed: {e}")

if __name__ == "__main__":
    test_api()
