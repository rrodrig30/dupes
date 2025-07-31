import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class that loads all settings from environment variables."""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    FLASK_APP = os.environ.get('FLASK_APP') or 'run.py'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Application Configuration
    HOST = os.environ.get('APP_HOST') or '127.0.0.1'
    PORT = int(os.environ.get('APP_PORT') or 5000)
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    
    # File Processing Configuration
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE') or 8192)  # 8KB chunks for file reading
    SUPPORTED_EXTENSIONS = os.environ.get('SUPPORTED_EXTENSIONS', '.txt,.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov,.zip,.rar,.7z').split(',')
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE') or 100 * 1024 * 1024)  # 100MB
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'
    LOG_FORMAT = os.environ.get('LOG_FORMAT') or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Performance Configuration
    MAX_WORKERS = int(os.environ.get('MAX_WORKERS') or 4)
    TIMEOUT_SECONDS = int(os.environ.get('TIMEOUT_SECONDS') or 300)
    
    @staticmethod
    def init_app(app):
        """Initialize the Flask application with configuration."""
        app.config.from_object(Config)
        
        # Ensure logs directory exists
        log_dir = os.path.dirname(Config.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)