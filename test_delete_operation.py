#!/usr/bin/env python3
"""
Test the delete operation for all entities
"""

import requests
import json

def test_delete_operation():
    """Test delete operation for different entities"""
    base_url = "http://localhost:8000"
    
    # Test data for different entities
    test_data = {
        "teachers": {
            "teacher_name": "Test Teacher DELETE",
            "email": "test.delete@example.com",
            "max_sessions_per_day": 2,
            "max_sessions_per_week": 10
        },
        "subjects": {
            "subject_name": "Test Subject DELETE",
            "teacher_id": 1,
            "sessions_per_week": 2,
            "is_lab": False
        },
        "batches": {
            "batch_name": "Test Batch DELETE",
            "department": "Test Department",
            "sem": "1",
            "academic_year": "2024-25"
        },
        "rooms": {
            "room_name": "Test Room DELETE",
            "capacity": 30,
            "room_type": "CLASSROOM",
            "assigned_batch_id": None
        }
    }
    
    for entity, data in test_data.items():
        print(f"\n🧪 Testing {entity} delete operation...")
        
        try:
            # Step 1: Create a test record
            create_response = requests.post(f"{base_url}/data/{entity}", json=data)
            if create_response.status_code != 200:
                print(f"❌ Failed to create test {entity}: {create_response.text}")
                continue
            
            created_item = create_response.json()
            item_id = None
            
            # Get the ID field based on entity
            id_fields = {
                "teachers": "teacher_id",
                "subjects": "subject_id", 
                "batches": "batch_id",
                "rooms": "room_id"
            }
            
            item_id = created_item.get(id_fields[entity])
            if not item_id:
                print(f"❌ Could not get ID for created {entity}")
                continue
            
            print(f"✅ Created test {entity} with ID: {item_id}")
            
            # Step 2: Delete the record
            delete_response = requests.delete(f"{base_url}/data/{entity}/{item_id}")
            if delete_response.status_code == 200:
                delete_result = delete_response.json()
                print(f"✅ Delete successful: {delete_result}")
                
                # Step 3: Verify the record is gone
                verify_response = requests.get(f"{base_url}/data/{entity}")
                if verify_response.status_code == 200:
                    all_items = verify_response.json()
                    item_exists = any(item.get(id_fields[entity]) == item_id for item in all_items)
                    
                    if not item_exists:
                        print(f"✅ {entity} delete operation SUCCESSFUL!")
                    else:
                        print(f"❌ {entity} still exists after delete")
                else:
                    print(f"❌ Could not verify {entity} deletion")
            else:
                print(f"❌ Delete failed: {delete_response.status_code} - {delete_response.text}")
                
        except Exception as e:
            print(f"❌ Test failed for {entity}: {e}")
    
    print(f"\n🎯 Delete operation testing completed!")

if __name__ == "__main__":
    test_delete_operation()
