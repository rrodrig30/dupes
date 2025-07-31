#!/usr/bin/env python3
"""
Test the delete functionality by creating test files and testing the delete endpoint
"""

import os
import sys
import json
import requests

# Add current directory to path for imports  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_duplicate():
    """Create an additional test duplicate file."""
    test_file_path = os.path.join(os.getcwd(), 'test_files', 'another_duplicate.txt')
    
    # Create the same content as our existing duplicates
    content = """This is a test file with some content.
It has multiple lines to make it interesting.
This file will be duplicated to test the functionality."""
    
    with open(test_file_path, 'w') as f:
        f.write(content)
    
    print(f"Created test duplicate: {test_file_path}")
    return test_file_path

def test_delete_functionality():
    """Test the delete functionality through the API."""
    
    # Create an additional test duplicate
    duplicate_path = create_test_duplicate()
    
    # Test the delete endpoint
    url = 'http://127.0.0.1:5000/delete-file'
    data = {
        'file_path': duplicate_path
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        
        print(f"Delete API Response Status: {response.status_code}")
        print(f"Delete API Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("[SUCCESS] Delete functionality working correctly!")
            print(f"[SUCCESS] File deleted: {duplicate_path}")
            print(f"[SUCCESS] Backup created: {result.get('backup_location')}")
            print(f"[SUCCESS] Space freed: {result.get('space_freed')} bytes")
            
            # Verify file was actually deleted
            if not os.path.exists(duplicate_path):
                print("[SUCCESS] File successfully removed from filesystem")
            else:
                print("[ERROR] File still exists on filesystem")
                
            # Verify backup was created
            backup_path = result.get('backup_location')
            if backup_path and os.path.exists(backup_path):
                print("[SUCCESS] Backup file successfully created")
            else:
                print("[ERROR] Backup file not found")
        else:
            print(f"[ERROR] Delete failed: {result.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the application. Make sure it's running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"[ERROR] Error testing delete functionality: {str(e)}")

def test_exit_functionality():
    """Test the exit functionality through the API."""
    url = 'http://127.0.0.1:5000/exit'
    
    try:
        response = requests.post(url)
        result = response.json()
        
        print(f"Exit API Response Status: {response.status_code}")
        print(f"Exit API Response: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("[SUCCESS] Exit functionality working correctly!")
            print("[SUCCESS] Application will shutdown gracefully")
        else:
            print(f"[ERROR] Exit failed: {result.get('error')}")
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to the application for exit test.")
    except Exception as e:
        print(f"[ERROR] Error testing exit functionality: {str(e)}")

if __name__ == '__main__':
    print("=== Testing Delete Functionality ===")
    test_delete_functionality()
    
    print("\n=== Testing Exit Functionality ===")
    print("Note: This will shut down the application!")
    response = input("Do you want to test the exit functionality? (y/N): ")
    if response.lower() == 'y':
        test_exit_functionality()
    else:
        print("Skipping exit test to keep application running.")