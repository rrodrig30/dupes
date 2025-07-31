import os
import hashlib
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from config import Config

class FileProcessor:
    """Handles file operations including scanning, hashing, and metadata extraction."""
    
    def __init__(self, directory_path: str):
        """Initialize FileProcessor with target directory path.
        
        Args:
            directory_path: Path to directory to process
        """
        self.directory_path = directory_path
        self.processed_files = []
        self.errors = []
        self.logger = logging.getLogger(__name__)
    
    def process_directory(self) -> Dict[str, List]:
        """Scan directory and generate file metadata with hashes.
        
        Returns:
            Dictionary containing processed files and any errors encountered
        """
        if not self._validate_directory():
            return {'files': [], 'errors': self.errors}
        
        self.logger.info(f"Starting directory scan: {self.directory_path}")
        
        for root, dirs, files in os.walk(self.directory_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                try:
                    if self._should_process_file(file_path):
                        file_info = self._process_single_file(file_path)
                        if file_info:
                            self.processed_files.append(file_info)
                except Exception as e:
                    error_msg = f"Error processing {file_path}: {str(e)}"
                    self.logger.warning(error_msg)
                    self.errors.append(error_msg)
        
        self.logger.info(f"Processed {len(self.processed_files)} files with {len(self.errors)} errors")
        return {'files': self.processed_files, 'errors': self.errors}
    
    def _validate_directory(self) -> bool:
        """Validate that directory path exists and is accessible.
        
        Returns:
            True if directory is valid, False otherwise
        """
        if not os.path.exists(self.directory_path):
            error_msg = f"Directory does not exist: {self.directory_path}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False
        
        if not os.path.isdir(self.directory_path):
            error_msg = f"Path is not a directory: {self.directory_path}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False
        
        if not os.access(self.directory_path, os.R_OK):
            error_msg = f"Directory is not readable: {self.directory_path}"
            self.logger.error(error_msg)
            self.errors.append(error_msg)
            return False
        
        return True
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed based on extension and size.
        
        Args:
            file_path: Path to file to check
            
        Returns:
            True if file should be processed, False otherwise
        """
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if Config.SUPPORTED_EXTENSIONS and ext not in Config.SUPPORTED_EXTENSIONS:
            return False
        
        # Check file size
        try:
            file_size = os.path.getsize(file_path)
            if file_size > Config.MAX_FILE_SIZE:
                self.logger.warning(f"File too large, skipping: {file_path} ({file_size} bytes)")
                return False
        except OSError:
            return False
        
        return True
    
    def _process_single_file(self, file_path: str) -> Optional[Dict]:
        """Process a single file to extract metadata and calculate hash.
        
        Args:
            file_path: Path to file to process
            
        Returns:
            Dictionary containing file metadata or None if processing failed
        """
        try:
            # Get file metadata
            stat_info = os.stat(file_path)
            file_size = stat_info.st_size
            modified_time = datetime.fromtimestamp(stat_info.st_mtime)
            
            # Calculate file hash
            file_hash = self.calculate_hash(file_path)
            if not file_hash:
                return None
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'modified': modified_time.isoformat(),
                'hash': file_hash,
                'extension': os.path.splitext(file_path)[1].lower()
            }
        
        except Exception as e:
            self.logger.error(f"Failed to process file {file_path}: {str(e)}")
            return None
    
    def calculate_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to file to hash
            
        Returns:
            SHA-256 hash as hexadecimal string or None if calculation failed
        """
        try:
            hash_sha256 = hashlib.sha256()
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(Config.CHUNK_SIZE):
                    hash_sha256.update(chunk)
            
            return hash_sha256.hexdigest()
        
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return None
        except PermissionError:
            self.logger.error(f"Permission denied: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Hash calculation failed for {file_path}: {str(e)}")
            return None
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict]:
        """Extract file metadata without calculating hash.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary containing file metadata or None if extraction failed
        """
        try:
            stat_info = os.stat(file_path)
            return {
                'size': stat_info.st_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
                'accessed': datetime.fromtimestamp(stat_info.st_atime).isoformat()
            }
        except Exception as e:
            self.logger.error(f"Failed to get metadata for {file_path}: {str(e)}")
            return None