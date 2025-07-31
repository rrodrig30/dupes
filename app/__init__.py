import logging
import os
from flask import Flask
from config import Config

def create_app():
    """Factory function to create Flask application instance."""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    Config.init_app(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints/routes
    from app.routes import main
    app.register_blueprint(main)
    
    return app

def setup_logging(app):
    """Configure application logging."""
    if not app.debug:
        # Ensure log directory exists
        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Setup file handler
        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
        app.logger.info('Duplicate File Detector startup')