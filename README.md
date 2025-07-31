# Duplicate File Detector

A powerful Flask-based web application for detecting and managing duplicate files on your system. This tool uses SHA-256 hashing to accurately identify duplicate files and provides an intuitive web interface for browsing, analyzing, and cleaning up your file system.

## Features

### Core Functionality
- **Accurate Duplicate Detection**: Uses SHA-256 hashing for content-based file comparison
- **Recursive Directory Scanning**: Scans all subdirectories automatically
- **Real-time Statistics**: Shows duplicate groups, file counts, and space wasted
- **Safe Operations**: Read-only scanning with no accidental file modifications

### User Interface
- **Professional Web Interface**: Modern Bootstrap 5 responsive design
- **Folder Browser**: Built-in folder browser that bypasses browser security restrictions
- **Interactive Navigation**: Click-through folder navigation with breadcrumbs
- **Real-time Validation**: Instant path validation with file/directory counts

### File Management
- **Individual Delete**: Delete specific duplicate files with confirmation
- **Bulk Delete**: Delete all duplicates at once with safety checks
- **Smart Protection**: Automatically preserves the oldest file as "original"
- **Permission Handling**: Comprehensive permission checking and error handling

### Technical Features
- **Environment Configuration**: Complete .env variable system
- **Comprehensive Logging**: Detailed logging with configurable levels
- **Error Handling**: Robust error handling with user-friendly messages
- **Performance Optimized**: Chunked file reading for memory efficiency

## Installation

### Prerequisites
- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Setup
1. **Clone the repository**
   ```bash
   git clone https://github.com/rrodrig30/dupes.git
   cd dupes
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional)**
   ```bash
   # Copy and modify .env file if needed
   cp .env .env.local
   # Edit .env.local with your preferred settings
   ```

## Usage

### Starting the Application
```bash
python run.py
```

The application will start on `http://127.0.0.1:5000` by default.

### Using the Web Interface

1. **Open your browser** and navigate to `http://127.0.0.1:5000`

2. **Select a directory** to scan:
   - **Type path manually**: Enter the full directory path
   - **Use folder browser**: Click "Browse" to navigate through your file system

3. **Start scanning**: Click "Start Scan" to begin duplicate detection

4. **Review results**: 
   - View duplicate groups organized by file content
   - See statistics showing space wasted and duplicate counts
   - Files marked with ⭐ are originals (oldest copies)

5. **Manage duplicates**:
   - **Delete individual files**: Click "Delete" on specific duplicate files
   - **Bulk delete**: Use "Delete All Duplicates" to remove all duplicates at once
   - **Export results**: Save scan results as JSON for record keeping

### API Endpoints

The application also provides REST API endpoints:

- `GET /api/browse-folders?path=<path>` - Browse folder contents
- `POST /api/validate-path` - Validate directory paths
- `POST /api/scan` - Programmatic directory scanning
- `POST /delete-file` - Delete individual files
- `POST /delete-duplicates` - Bulk delete operations

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key settings include:

```bash
# Flask Configuration
FLASK_DEBUG=True
SECRET_KEY=your-secret-key

# Application Settings
APP_HOST=127.0.0.1
APP_PORT=5000
MAX_CONTENT_LENGTH=16777216

# File Processing
CHUNK_SIZE=8192
MAX_FILE_SIZE=104857600

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### File Types

By default, the application processes common file types. You can configure supported extensions:

```bash
SUPPORTED_EXTENSIONS=.txt,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov,.zip,.rar,.7z
```

## Project Structure

```
dupes/
├── app/
│   ├── __init__.py          # Flask application factory
│   └── routes.py            # Web routes and API endpoints
├── utils/
│   ├── file_processor.py    # File scanning and hashing
│   └── duplicate_manager.py # Duplicate detection logic
├── templates/               # HTML templates
│   ├── base.html           # Base template with navigation
│   ├── index.html          # Home page with folder browser
│   ├── results.html        # Results display with statistics
│   ├── about.html          # Application information
│   ├── 404.html            # Error pages
│   └── 500.html
├── static/                 # Static assets (CSS, JS, images)
├── logs/                   # Application logs
├── config.py              # Configuration management
├── run.py                 # Application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## Development

### Running Tests

The project includes comprehensive tests:

```bash
# Test core functionality
python test_functionality.py

# Test delete operations
python test_improved_delete.py

# Test folder browsing
python test_folder_browsing.py
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Follow PEP 8 guidelines
- Use descriptive variable names
- Include docstrings for all public methods
- Add type hints where appropriate
- Maintain comprehensive error handling

## Security Considerations

- **Read-only Operations**: The scanner only reads files, never modifies them
- **Permission Checking**: Comprehensive permission validation before operations
- **Path Validation**: Server-side path validation prevents directory traversal
- **User Confirmations**: Multiple confirmation dialogs for destructive operations
- **Local Processing**: All processing happens locally, no data sent externally

## Performance

### Optimization Features
- **Chunked Reading**: Files are read in 8KB chunks to minimize memory usage
- **Efficient Hashing**: SHA-256 implementation optimized for large files
- **Smart Filtering**: Pre-filtering by file size before hash calculation
- **Concurrent Safe**: Thread-safe operations for future multi-threading

### System Requirements
- **RAM**: Minimum 512MB, recommended 2GB+
- **Storage**: Minimal storage footprint (< 50MB)
- **CPU**: Any modern processor (hash calculation is CPU-intensive)

## Troubleshooting

### Common Issues

**Application won't start**
- Check Python version (3.8+ required)
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check port availability (default: 5000)

**Permission errors**
- Run with appropriate permissions for target directories
- Check directory read permissions
- Verify antivirus software isn't blocking access

**Browser security warnings**
- Use the built-in folder browser instead of manual path entry
- Ensure you're accessing via `http://127.0.0.1:5000` not `localhost`

**Performance issues**
- Reduce `CHUNK_SIZE` for systems with limited RAM
- Set `MAX_FILE_SIZE` to skip very large files
- Use `LOG_LEVEL=WARNING` to reduce logging overhead

### Getting Help

If you encounter issues:

1. Check the application logs in `logs/app.log`
2. Review the console output for error messages
3. Verify your configuration in `.env`
4. Test with a small directory first
5. Open an issue on GitHub with detailed information

## License

This project is open source and available under the [MIT License](LICENSE).

## Changelog

### Version 1.0.0
- Initial release with complete duplicate detection functionality
- Web-based folder browser with security bypass
- Individual and bulk file deletion capabilities
- Professional responsive web interface
- Comprehensive error handling and logging
- Environment-based configuration system
- Full test suite with API endpoint testing

---

**Note**: This application is designed for local use and includes safety features to prevent accidental data loss. Always review duplicate detection results carefully before deleting files.