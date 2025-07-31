import logging
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from datetime import datetime

class DuplicateManager:
    """Manages duplicate detection and reporting for processed files."""
    
    def __init__(self):
        """Initialize DuplicateManager."""
        self.hash_map = defaultdict(list)
        self.duplicates = {}
        self.stats = {
            'total_files': 0,
            'duplicate_groups': 0,
            'duplicate_files': 0,
            'space_wasted': 0
        }
        self.logger = logging.getLogger(__name__)
    
    def find_duplicates(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify duplicate files based on SHA-256 hashes.
        
        Args:
            files: List of file metadata dictionaries
            
        Returns:
            Dictionary mapping hashes to lists of duplicate files
        """
        self.logger.info(f"Analyzing {len(files)} files for duplicates")
        self._build_hash_map(files)
        self._identify_duplicates()
        self._calculate_statistics()
        
        self.logger.info(f"Found {self.stats['duplicate_groups']} duplicate groups "
                        f"containing {self.stats['duplicate_files']} duplicate files")
        
        return self.duplicates
    
    def _build_hash_map(self, files: List[Dict]) -> None:
        """Build mapping of file hashes to file information.
        
        Args:
            files: List of file metadata dictionaries
        """
        self.hash_map.clear()
        self.stats['total_files'] = len(files)
        
        for file_info in files:
            file_hash = file_info.get('hash')
            if file_hash:
                self.hash_map[file_hash].append(file_info)
    
    def _identify_duplicates(self) -> None:
        """Identify hash collisions (duplicate files)."""
        self.duplicates.clear()
        
        for file_hash, file_list in self.hash_map.items():
            if len(file_list) > 1:
                # Sort by modification time (oldest first)
                sorted_files = sorted(file_list, key=lambda f: f.get('modified', ''))
                self.duplicates[file_hash] = sorted_files
    
    def _calculate_statistics(self) -> None:
        """Calculate duplicate statistics."""
        self.stats['duplicate_groups'] = len(self.duplicates)
        self.stats['duplicate_files'] = 0
        self.stats['space_wasted'] = 0
        
        for file_hash, file_list in self.duplicates.items():
            # Count all but the first file as duplicates
            duplicate_count = len(file_list) - 1
            self.stats['duplicate_files'] += duplicate_count
            
            # Calculate wasted space (size of duplicates)
            if file_list:
                file_size = file_list[0].get('size', 0)
                self.stats['space_wasted'] += file_size * duplicate_count
    
    def group_files_by_hash(self, files: List[Dict]) -> Dict[str, List[Dict]]:
        """Group all files by their calculated hashes.
        
        Args:
            files: List of file metadata dictionaries
            
        Returns:
            Dictionary mapping hashes to lists of files
        """
        grouped = defaultdict(list)
        
        for file_info in files:
            file_hash = file_info.get('hash')
            if file_hash:
                grouped[file_hash].append(file_info)
        
        return dict(grouped)
    
    def generate_report(self, duplicates: Dict[str, List[Dict]] = None) -> Dict:
        """Generate structured report of duplicate files.
        
        Args:
            duplicates: Optional duplicate dictionary, uses internal if not provided
            
        Returns:
            Comprehensive duplicate report dictionary
        """
        if duplicates is None:
            duplicates = self.duplicates
        
        report = {
            'summary': dict(self.stats),
            'timestamp': datetime.now().isoformat(),
            'duplicate_groups': []
        }
        
        for file_hash, file_list in duplicates.items():
            if len(file_list) > 1:
                group_info = {
                    'hash': file_hash,
                    'file_count': len(file_list),
                    'file_size': file_list[0].get('size', 0),
                    'total_size': file_list[0].get('size', 0) * len(file_list),
                    'wasted_space': file_list[0].get('size', 0) * (len(file_list) - 1),
                    'files': []
                }
                
                for i, file_info in enumerate(file_list):
                    file_entry = {
                        'path': file_info.get('path', ''),
                        'name': file_info.get('name', ''),
                        'size': file_info.get('size', 0),
                        'modified': file_info.get('modified', ''),
                        'is_original': i == 0,  # First file is considered original
                        'extension': file_info.get('extension', '')
                    }
                    group_info['files'].append(file_entry)
                
                report['duplicate_groups'].append(group_info)
        
        # Sort groups by wasted space (descending)
        report['duplicate_groups'].sort(key=lambda g: g['wasted_space'], reverse=True)
        
        return report
    
    def get_statistics(self) -> Dict:
        """Get current duplicate detection statistics.
        
        Returns:
            Dictionary containing statistics
        """
        return dict(self.stats)
    
    def find_duplicates_by_size(self, files: List[Dict]) -> Dict[int, List[Dict]]:
        """Find potential duplicates by file size (faster initial filter).
        
        Args:
            files: List of file metadata dictionaries
            
        Returns:
            Dictionary mapping file sizes to lists of files
        """
        size_groups = defaultdict(list)
        
        for file_info in files:
            file_size = file_info.get('size', 0)
            if file_size > 0:  # Skip empty files
                size_groups[file_size].append(file_info)
        
        # Return only groups with multiple files
        return {size: file_list for size, file_list in size_groups.items() 
                if len(file_list) > 1}
    
    def suggest_deletions(self, duplicates: Dict[str, List[Dict]] = None) -> List[Dict]:
        """Suggest which duplicate files could be safely deleted.
        
        Args:
            duplicates: Optional duplicate dictionary, uses internal if not provided
            
        Returns:
            List of suggested files for deletion with reasoning
        """
        if duplicates is None:
            duplicates = self.duplicates
        
        suggestions = []
        
        for file_hash, file_list in duplicates.items():
            if len(file_list) <= 1:
                continue
            
            # Sort by modification time (keep oldest as original)
            sorted_files = sorted(file_list, key=lambda f: f.get('modified', ''))
            
            # Suggest deletion of all but the first (oldest) file
            for file_info in sorted_files[1:]:
                suggestion = {
                    'file_path': file_info.get('path', ''),
                    'file_name': file_info.get('name', ''),
                    'file_size': file_info.get('size', 0),
                    'reason': 'Duplicate of older file',
                    'original_path': sorted_files[0].get('path', ''),
                    'space_saved': file_info.get('size', 0)
                }
                suggestions.append(suggestion)
        
        # Sort by space saved (descending)
        suggestions.sort(key=lambda s: s['space_saved'], reverse=True)
        
        return suggestions