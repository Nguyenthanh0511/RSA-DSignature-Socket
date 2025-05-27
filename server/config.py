# server/config.py
"""
Application configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Server
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///secure_transfer.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'txt,pdf,png,jpg,jpeg,gif,doc,docx,json,xml').split(','))
    
    # Security
    RSA_KEY_SIZE = int(os.environ.get('RSA_KEY_SIZE', 2048))
    SESSION_TIMEOUT = int(os.environ.get('SESSION_TIMEOUT', 3600))
    
    # Keys Directory
    SERVER_KEYS_DIR = os.environ.get('SERVER_KEYS_DIR', 'keys/server')
    CLIENT_KEYS_DIR = os.environ.get('CLIENT_KEYS_DIR', 'keys/client')
    
    # CORS
    CORS_ORIGINS = "*"  # In production, specify actual origins
    
    
class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    
    
class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add more production-specific settings
    
    
class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    
# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}