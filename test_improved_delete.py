#!/usr/bin/env python3
"""
Test the improved delete functionality (no backups, no hanging)
"""

import os
import sys
import json
import requests
import time

# Add current directory to path for imports  
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_files():
    """Create multiple test duplicate files for testing."""
    test_files = []
    base_content = """This is a test file for testing delete functionality.
It has some content to make it a reasonable size.
This will be used to test that deletion works without hanging."""
    
    # Create test files
    for i in range(3):
        test_file_path = os.path.join(os.getcwd(), 'test_files', f'test_delete_{i}.txt')
        with open(test_file_path, 'w') as f:
            f.write(base_content)
        test_files.append(test_file_path)
        print(f"Created test file: {test_file_path}")
    
    return test_files

def test_single_delete():
    """Test deleting a single file without hanging."""
    print("\n=== Testing Single File Delete ===")
    
    # Create a test file
    test_files = create_test_files()
    test_file = test_files[0]
    
    url = 'http://127.0.0.1:5000/delete-file'
    data = {'file_path': test_file}
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=10)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("[SUCCESS] Single file delete completed without hanging!")
                print(f"[SUCCESS] File deleted: {test_file}")
                print(f"[SUCCESS] Space freed: {result.get('space_freed')} bytes")
                
                # Verify file was deleted
                if not os.path.exists(test_file):
                    print("[SUCCESS] File successfully removed from filesystem")
                else:
                    print("[ERROR] File still exists on filesystem")
            else:
                print(f"[ERROR] Delete failed: {result.get('error')}")
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - hanging issue still exists")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to application")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")

def test_bulk_delete():
    """Test deleting multiple files without hanging."""
    print("\n=== Testing Bulk File Delete ===")
    
    # Create test files (use remaining files from previous test)
    existing_files = [f for f in [
        os.path.join(os.getcwd(), 'test_files', 'test_delete_1.txt'),
        os.path.join(os.getcwd(), 'test_files', 'test_delete_2.txt')
    ] if os.path.exists(f)]
    
    if not existing_files:
        # Create new files if none exist
        test_files = create_test_files()
        existing_files = test_files[1:3]  # Use last two files
    
    url = 'http://127.0.0.1:5000/delete-duplicates'
    data = {'file_paths': existing_files}
    
    try:
        start_time = time.time()
        response = requests.post(url, json=data, timeout=15)
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print("[SUCCESS] Bulk delete completed without hanging!")
                print(f"[SUCCESS] Files deleted: {result.get('deleted_count')}")
                print(f"[SUCCESS] Total space freed: {result.get('total_space_freed')} bytes")
                
                # Verify files were deleted
                remaining_files = [f for f in existing_files if os.path.exists(f)]
                if not remaining_files:
                    print("[SUCCESS] All files successfully removed from filesystem")
                else:
                    print(f"[WARNING] Some files still exist: {remaining_files}")
            else:
                print(f"[ERROR] Bulk delete failed: {result.get('error')}")
        else:
            print(f"[ERROR] HTTP Error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("[ERROR] Request timed out - hanging issue still exists")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Could not connect to application")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")

def cleanup_test_files():
    """Clean up any remaining test files."""
    print("\n=== Cleaning Up Test Files ===")
    test_patterns = ['test_delete_', 'another_duplicate.txt']
    
    for pattern in test_patterns:
        for i in range(5):  # Check for multiple numbered files
            test_file = os.path.join(os.getcwd(), 'test_files', f'{pattern}{i}.txt' if pattern.endswith('_') else pattern)
            if os.path.exists(test_file):
                try:
                    os.remove(test_file)
                    print(f"Cleaned up: {test_file}")
                except Exception as e:
                    print(f"Failed to clean up {test_file}: {str(e)}")

if __name__ == '__main__':
    print("=== Testing Improved Delete Functionality ===")
    print("This test verifies that delete operations complete without hanging")
    
    test_single_delete()
    test_bulk_delete()
    cleanup_test_files()
    
    print("\n=== Test Complete ===")
    print("If no timeout errors occurred, the hanging issue has been resolved!")