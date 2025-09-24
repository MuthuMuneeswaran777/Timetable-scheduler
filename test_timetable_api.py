#!/usr/bin/env python3
"""
Test the timetable API endpoints
"""

import requests
import json

def test_timetable_api():
    """Test the timetable API endpoints"""
    base_url = "http://localhost:8000"
    
    try:
        # Test timetables list endpoint
        print("Testing timetables list endpoint...")
        response = requests.get(f"{base_url}/timetables")
        print(f"Timetables list: {response.status_code}")
        if response.status_code == 200:
            timetables = response.json()
            print(f"Found {len(timetables)} timetables")
        else:
            print(f"Error: {response.text}")
        
        # Test batches endpoint to get a valid batch_id
        print("\nTesting batches endpoint...")
        response = requests.get(f"{base_url}/data/batches")
        print(f"Batches list: {response.status_code}")
        if response.status_code == 200:
            batches = response.json()
            print(f"Found {len(batches)} batches")
            if batches:
                batch_id = batches[0].get('batch_id', 1)
                print(f"Using batch_id: {batch_id}")
            else:
                batch_id = 1
                print("No batches found, using batch_id: 1")
        else:
            batch_id = 1
            print(f"Error getting batches: {response.text}")
            print("Using default batch_id: 1")
        
        # Test timetable generation
        print(f"\nTesting timetable generation for batch {batch_id}...")
        response = requests.post(f"{base_url}/timetables/generate", params={"batch_id": batch_id})
        print(f"Generate timetable: {response.status_code}")
        if response.status_code == 200:
            timetable = response.json()
            print(f"Generated timetable: {timetable}")
            
            # Test getting the generated timetable
            timetable_id = timetable.get("timetable_id")
            if timetable_id:
                print(f"\nTesting get timetable {timetable_id}...")
                response = requests.get(f"{base_url}/timetables/{timetable_id}")
                print(f"Get timetable: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"Timetable entries: {len(data.get('entries', []))}")
                else:
                    print(f"Error getting timetable: {response.text}")
        else:
            print(f"Error generating timetable: {response.text}")
            
    except Exception as e:
        print(f"API test failed: {e}")

if __name__ == "__main__":
    test_timetable_api()
