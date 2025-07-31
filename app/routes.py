import os
import logging
import signal
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_processor import FileProcessor
from utils.duplicate_manager import DuplicateManager

main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main.route('/')
def index():
    """Home page with directory selection form."""
    return render_template('index.html')

@main.route('/scan', methods=['POST'])
def scan_directory():
    """Handle directory scanning request."""
    try:
        # Get directory path from form
        directory_path = request.form.get('directory', '').strip()
        
        if not directory_path:
            flash('Please provide a directory path', 'error')
            return redirect(url_for('main.index'))
        
        # Validate directory path
        if not os.path.exists(directory_path):
            flash('Directory does not exist', 'error')
            return redirect(url_for('main.index'))
        
        if not os.path.isdir(directory_path):
            flash('Path is not a directory', 'error')
            return redirect(url_for('main.index'))
        
        logger.info(f"Starting scan of directory: {directory_path}")
        
        # Process directory
        processor = FileProcessor(directory_path)
        result = processor.process_directory()
        
        if not result['files']:
            flash('No files found or processed in the specified directory', 'warning')
            return redirect(url_for('main.index'))
        
        # Find duplicates
        manager = DuplicateManager()
        duplicates = manager.find_duplicates(result['files'])
        
        # Generate report
        report = manager.generate_report(duplicates)
        
        logger.info(f"Scan completed. Found {len(duplicates)} duplicate groups")
        
        return render_template('results.html', 
                             report=report, 
                             directory=directory_path,
                             errors=result['errors'])
    
    except Exception as e:
        logger.error(f"Scan error: {str(e)}", exc_info=True)
        flash(f'An error occurred during scanning: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@main.route('/api/scan', methods=['POST'])
def api_scan_directory():
    """API endpoint for directory scanning."""
    try:
        data = request.get_json()
        
        if not data or 'directory' not in data:
            return jsonify({'error': 'Directory path is required'}), 400
        
        directory_path = data['directory'].strip()
        
        if not os.path.exists(directory_path):
            return jsonify({'error': 'Directory does not exist'}), 400
        
        if not os.path.isdir(directory_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        logger.info(f"API scan request for directory: {directory_path}")
        
        # Process directory
        processor = FileProcessor(directory_path)
        result = processor.process_directory()
        
        # Find duplicates
        manager = DuplicateManager()
        duplicates = manager.find_duplicates(result['files'])
        
        # Generate report
        report = manager.generate_report(duplicates)
        
        # Add additional API-specific information
        response_data = {
            'success': True,
            'directory': directory_path,
            'report': report,
            'processing_errors': result['errors']
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"API scan error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Scanning failed: {str(e)}'}), 500

@main.route('/api/suggestions/<path:directory>')
def api_get_suggestions(directory):
    """API endpoint to get deletion suggestions for a directory."""
    try:
        if not os.path.exists(directory):
            return jsonify({'error': 'Directory does not exist'}), 400
        
        # Process directory
        processor = FileProcessor(directory)
        result = processor.process_directory()
        
        # Find duplicates
        manager = DuplicateManager()
        duplicates = manager.find_duplicates(result['files'])
        
        # Get deletion suggestions
        suggestions = manager.suggest_deletions(duplicates)
        
        return jsonify({
            'success': True,
            'directory': directory,
            'suggestions': suggestions,
            'total_space_saved': sum(s['space_saved'] for s in suggestions)
        })
    
    except Exception as e:
        logger.error(f"API suggestions error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to generate suggestions: {str(e)}'}), 500

@main.route('/about')
def about():
    """About page with application information."""
    return render_template('about.html')

@main.route('/api/browse-folders', methods=['GET'])
def browse_folders():
    """API endpoint to browse folders on the server."""
    try:
        # Get the requested path, default to user home or root drives
        requested_path = request.args.get('path', '')
        
        if not requested_path:
            # Return available drives/root directories
            if os.name == 'nt':  # Windows
                import string
                drives = []
                for letter in string.ascii_uppercase:
                    drive_path = f"{letter}:\\"
                    if os.path.exists(drive_path):
                        drives.append({
                            'name': f"Drive {letter}:",
                            'path': drive_path,
                            'type': 'drive',
                            'accessible': True
                        })
                return jsonify({
                    'success': True,
                    'current_path': '',
                    'parent_path': None,
                    'items': drives
                })
            else:  # Unix-like systems
                requested_path = os.path.expanduser('~')
        
        # Validate and normalize the path
        if not os.path.exists(requested_path):
            return jsonify({'error': 'Path does not exist'}), 404
            
        if not os.path.isdir(requested_path):
            return jsonify({'error': 'Path is not a directory'}), 400
        
        try:
            # Get directory contents
            items = []
            
            # Add parent directory link if not at root
            parent_path = os.path.dirname(requested_path)
            if parent_path != requested_path:  # Not at root
                items.append({
                    'name': '.. (Parent Directory)',
                    'path': parent_path,
                    'type': 'parent',
                    'accessible': True
                })
            
            # List directory contents
            for item_name in sorted(os.listdir(requested_path)):
                item_path = os.path.join(requested_path, item_name)
                
                try:
                    if os.path.isdir(item_path):
                        # Check if directory is accessible
                        accessible = os.access(item_path, os.R_OK)
                        
                        items.append({
                            'name': item_name,
                            'path': item_path,
                            'type': 'folder',
                            'accessible': accessible
                        })
                except (PermissionError, OSError):
                    # Skip inaccessible items
                    continue
            
            return jsonify({
                'success': True,
                'current_path': requested_path,
                'parent_path': parent_path if parent_path != requested_path else None,
                'items': items
            })
            
        except PermissionError:
            return jsonify({'error': 'Permission denied accessing directory'}), 403
        except Exception as e:
            logger.error(f"Error browsing directory {requested_path}: {str(e)}")
            return jsonify({'error': f'Failed to browse directory: {str(e)}'}), 500
    
    except Exception as e:
        logger.error(f"Error in browse_folders: {str(e)}", exc_info=True)
        return jsonify({'error': f'Browse operation failed: {str(e)}'}), 500

@main.route('/api/validate-path', methods=['POST'])
def validate_path():
    """Validate if a path exists and is accessible."""
    try:
        data = request.get_json()
        if not data or 'path' not in data:
            return jsonify({'error': 'Path is required'}), 400
        
        path = data['path']
        
        if not os.path.exists(path):
            return jsonify({
                'valid': False,
                'error': 'Path does not exist'
            })
        
        if not os.path.isdir(path):
            return jsonify({
                'valid': False,
                'error': 'Path is not a directory'
            })
        
        if not os.access(path, os.R_OK):
            return jsonify({
                'valid': False,
                'error': 'Permission denied - directory not readable'
            })
        
        # Try to list contents to verify full access
        try:
            file_count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
            dir_count = len([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
            
            return jsonify({
                'valid': True,
                'path': path,
                'file_count': file_count,
                'dir_count': dir_count
            })
        except Exception:
            return jsonify({
                'valid': False,
                'error': 'Directory exists but contents cannot be accessed'
            })
    
    except Exception as e:
        logger.error(f"Error validating path: {str(e)}", exc_info=True)
        return jsonify({'error': f'Path validation failed: {str(e)}'}), 500

@main.route('/delete-file', methods=['POST'])
def delete_file():
    """Delete a specific duplicate file."""
    try:
        data = request.get_json()
        if not data or 'file_path' not in data:
            return jsonify({'error': 'File path is required'}), 400
        
        file_path = data['file_path']
        
        # Validate file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'File does not exist'}), 404
        
        # Get file info before deletion
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        
        # Delete the file
        os.remove(file_path)
        logger.info(f"Deleted duplicate file: {file_path}")
        
        return jsonify({
            'success': True,
            'message': f'File "{file_name}" deleted successfully',
            'space_freed': file_size
        })
        
    except PermissionError:
        logger.error(f"Permission denied deleting {file_path}")
        return jsonify({'error': 'Permission denied. Cannot delete file.'}), 403
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}", exc_info=True)
        return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

@main.route('/delete-duplicates', methods=['POST'])
def delete_duplicates():
    """Delete multiple duplicate files."""
    try:
        data = request.get_json()
        if not data or 'file_paths' not in data:
            return jsonify({'error': 'File paths are required'}), 400
        
        file_paths = data['file_paths']
        if not isinstance(file_paths, list):
            return jsonify({'error': 'File paths must be a list'}), 400
        
        deleted_files = []
        total_space_freed = 0
        errors = []
        
        for file_path in file_paths:
            try:
                if not os.path.exists(file_path):
                    errors.append(f"File not found: {file_path}")
                    continue
                
                # Get file info
                file_size = os.path.getsize(file_path)
                file_name = os.path.basename(file_path)
                
                # Delete file
                os.remove(file_path)
                
                deleted_files.append({
                    'path': file_path,
                    'name': file_name,
                    'size': file_size
                })
                total_space_freed += file_size
                
                logger.info(f"Deleted duplicate: {file_path}")
                
            except Exception as e:
                error_msg = f"Failed to delete {file_path}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return jsonify({
            'success': True,
            'deleted_count': len(deleted_files),
            'deleted_files': deleted_files,
            'total_space_freed': total_space_freed,
            'errors': errors
        })
        
    except Exception as e:
        logger.error(f"Error in bulk delete: {str(e)}", exc_info=True)
        return jsonify({'error': f'Bulk delete failed: {str(e)}'}), 500

@main.route('/exit', methods=['POST'])
def exit_application():
    """Gracefully exit the application."""
    try:
        logger.info("Application shutdown requested by user")
        
        # Send shutdown signal without cleanup to avoid hanging
        def shutdown_server():
            import threading
            def kill_server():
                import time
                time.sleep(0.5)  # Shorter delay to prevent hanging
                os.kill(os.getpid(), signal.SIGTERM)
            
            thread = threading.Thread(target=kill_server)
            thread.daemon = True
            thread.start()
        
        shutdown_server()
        
        return jsonify({
            'success': True,
            'message': 'Application is shutting down...'
        })
        
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)
        return jsonify({'error': f'Shutdown failed: {str(e)}'}), 500

@main.errorhandler(404)
def page_not_found(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return render_template('500.html'), 500

def format_file_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

# Make format_file_size available in templates
@main.app_template_filter('filesize')
def filesize_filter(size_bytes):
    """Template filter for formatting file sizes."""
    return format_file_size(size_bytes)