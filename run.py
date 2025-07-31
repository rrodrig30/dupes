#!/usr/bin/env python3
"""
Duplicate File Detector - Main Entry Point

A Flask-based web application for detecting duplicate files in directories.
Uses SHA-256 hashing for accurate duplicate detection.
"""

import os
import sys
import logging
from app import create_app
from config import Config

def setup_logging():
    """Configure application logging."""
    # Ensure logs directory exists
    log_dir = os.path.dirname(Config.LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main entry point of the application."""
    try:
        # Setup logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        # Create Flask application
        app = create_app()
        
        logger.info("Starting Duplicate File Detector application")
        logger.info(f"Configuration: Host={Config.HOST}, Port={Config.PORT}, Debug={Config.FLASK_DEBUG}")
        
        # Run the application
        app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.FLASK_DEBUG,
            threaded=True
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()