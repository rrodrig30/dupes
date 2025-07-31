#!/usr/bin/env python3
"""
Test the folder browsing functionality
"""

import requests
import json
import os

def test_browse_folders_api():
    """Test the folder browsing API endpoints."""
    print("=== Testing Folder Browsing API ===")
    
    # Test 1: Get root folders/drives
    print("\n1. Testing root folder listing...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/browse-folders')
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if data.get('success'):
            print(f"[SUCCESS] Found {len(data.get('items', []))} root items")
            
            # Test navigation to first available drive/folder
            if data.get('items'):
                first_item = data['items'][0]
                if first_item.get('accessible'):
                    test_path = first_item['path']
                    print(f"\n2. Testing navigation to: {test_path}")
                    
                    response2 = requests.get(f'http://127.0.0.1:5000/api/browse-folders?path={test_path}')
                    data2 = response2.json()
                    
                    print(f"Status Code: {response2.status_code}")
                    print(f"Items found: {len(data2.get('items', []))}")
                    
                    if data2.get('success'):
                        print("[SUCCESS] Successfully navigated to folder")
                    else:
                        print(f"[ERROR] Navigation failed: {data2.get('error')}")
        else:
            print(f"[ERROR] Root listing failed: {data.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] API test failed: {str(e)}")

def test_path_validation():
    """Test the path validation API."""
    print("\n=== Testing Path Validation API ===")
    
    # Test with a known valid path
    test_paths = [
        os.getcwd(),  # Current working directory
        "C:\\Windows" if os.name == 'nt' else "/tmp",  # System directory
        "nonexistent_path_12345"  # Invalid path
    ]
    
    for test_path in test_paths:
        print(f"\nTesting path: {test_path}")
        
        try:
            response = requests.post(
                'http://127.0.0.1:5000/api/validate-path',
                json={'path': test_path}
            )
            data = response.json()
            
            print(f"Status Code: {response.status_code}")
            print(f"Valid: {data.get('valid')}")
            
            if data.get('valid'):
                print(f"File count: {data.get('file_count')}")
                print(f"Directory count: {data.get('dir_count')}")
                print("[SUCCESS] Path validation working")
            else:
                print(f"Error: {data.get('error')}")
                if test_path == "nonexistent_path_12345":
                    print("[SUCCESS] Correctly identified invalid path")
                    
        except Exception as e:
            print(f"[ERROR] Validation test failed: {str(e)}")

def test_specific_directory():
    """Test browsing a specific directory."""
    print("\n=== Testing Specific Directory Browse ===")
    
    # Test browsing the project directory
    project_dir = os.getcwd()
    print(f"Testing project directory: {project_dir}")
    
    try:
        response = requests.get(f'http://127.0.0.1:5000/api/browse-folders?path={project_dir}')
        data = response.json()
        
        print(f"Status Code: {response.status_code}")
        
        if data.get('success'):
            print(f"[SUCCESS] Found {len(data.get('items', []))} items in project directory")
            print(f"Current path: {data.get('current_path')}")
            
            # List first few items
            items = data.get('items', [])[:5]  # First 5 items
            for item in items:
                print(f"  - {item['name']} ({item['type']}) - {'accessible' if item['accessible'] else 'locked'}")
                
        else:
            print(f"[ERROR] Directory browse failed: {data.get('error')}")
            
    except Exception as e:
        print(f"[ERROR] Directory test failed: {str(e)}")

if __name__ == '__main__':
    print("Testing Folder Browsing Functionality")
    print("=====================================")
    
    try:
        # Test if server is running
        response = requests.get('http://127.0.0.1:5000/', timeout=5)
        print("[SUCCESS] Server is running and accessible")
        
        test_browse_folders_api()
        test_path_validation()
        test_specific_directory()
        
        print("\n=== Test Summary ===")
        print("Folder browsing functionality tests completed.")
        print("Check the output above for any errors.")
        print("\nTo test the UI:")
        print("1. Open http://127.0.0.1:5000 in your browser")
        print("2. Click the 'Browse' button next to the directory field")
        print("3. Navigate through folders using the modal browser")
        
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to server at http://127.0.0.1:5000")
        print("Please make sure the Flask application is running.")
    except Exception as e:
        print(f"[ERROR] Test setup failed: {str(e)}")