#!/usr/bin/env python3
"""
Quick test of the duplicate detection functionality
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.file_processor import FileProcessor
from utils.duplicate_manager import DuplicateManager

def test_duplicate_detection():
    """Test the duplicate detection with test files."""
    print("Testing Duplicate File Detection...")
    
    # Test directory
    test_dir = os.path.join(os.getcwd(), 'test_files')
    
    if not os.path.exists(test_dir):
        print(f"Test directory {test_dir} does not exist!")
        return False
    
    print(f"Scanning directory: {test_dir}")
    
    # Process files
    processor = FileProcessor(test_dir)
    result = processor.process_directory()
    
    print(f"Processed {len(result['files'])} files")
    print(f"Encountered {len(result['errors'])} errors")
    
    if result['errors']:
        print("Errors:")
        for error in result['errors']:
            print(f"  - {error}")
    
    # Find duplicates
    manager = DuplicateManager()
    duplicates = manager.find_duplicates(result['files'])
    
    print(f"Found {len(duplicates)} duplicate groups")
    
    # Generate report
    report = manager.generate_report(duplicates)
    
    print("\n=== SCAN RESULTS ===")
    print(f"Total files: {report['summary']['total_files']}")
    print(f"Duplicate groups: {report['summary']['duplicate_groups']}")
    print(f"Duplicate files: {report['summary']['duplicate_files']}")
    print(f"Space wasted: {report['summary']['space_wasted']} bytes")
    
    if report['duplicate_groups']:
        print("\n=== DUPLICATE GROUPS ===")
        for i, group in enumerate(report['duplicate_groups'], 1):
            print(f"\nGroup {i}:")
            print(f"  Hash: {group['hash'][:16]}...")
            print(f"  File count: {group['file_count']}")
            print(f"  File size: {group['file_size']} bytes")
            print(f"  Files:")
            for file_info in group['files']:
                original_marker = " (ORIGINAL)" if file_info['is_original'] else ""
                print(f"    - {file_info['name']}{original_marker}")
                print(f"      Path: {file_info['path']}")
    
    return True

if __name__ == '__main__':
    success = test_duplicate_detection()
    sys.exit(0 if success else 1)