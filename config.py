"""
Flask application configuration
Environment-based setup with sensible defaults
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', False)
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///b2study.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        hours=int(os.getenv('SESSION_TIMEOUT', 3600)) // 3600
    )
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_UPLOAD_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 52428800))  # 50MB
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,doc,docx,xls,xlsx,ppt,pptx,zip').split(','))
    MAX_CONTENT_LENGTH = MAX_UPLOAD_SIZE
    
    # Export configuration
    EXPORT_FOLDER = os.getenv('EXPORT_FOLDER', 'exports')
    MAX_EXPORT_SIZE = int(os.getenv('MAX_EXPORT_SIZE', 10000))
    
    # Pagination
    ITEMS_PER_PAGE = int(os.getenv('ITEMS_PER_PAGE', 12))
    
    # Social links
    SOCIAL_LINKS = {
        'instagram': os.getenv('INSTAGRAM_URL', '#'),
        'linkedin': os.getenv('LINKEDIN_URL', '#'),
        'github': os.getenv('GITHUB_URL', '#'),
        'twitter': os.getenv('TWITTER_URL', '#'),
        'portfolio': os.getenv('PORTFOLIO_URL', '#'),
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
