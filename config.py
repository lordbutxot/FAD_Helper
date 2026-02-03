"""
Production-ready configuration for F.A.D. Helper
Supports both SQLite (local development) and PostgreSQL (production/Render)
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database - Support both local dev and production
    # Get DATABASE_URL and process it
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url:
        # Production: PostgreSQL on Render/Supabase
        # Convert postgres:// to postgresql:// (SQLAlchemy 1.4+ requires this)
        if _db_url.startswith('postgres://'):
            _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        
        # Supabase requires SSL. Append to URL if needed.
        if 'supabase.co' in _db_url and '?sslmode=' not in _db_url:
            _db_url = _db_url + '?sslmode=require'
        
        SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Local development: SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///fad_lists.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    
    # Session configuration
    # Note: SESSION_COOKIE_SECURE = True requires HTTPS - set to False if getting cookie issues
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'  # True in production, False in dev
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)  # Extended to 12 hours for better UX
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # File uploads
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB max file size
    UPLOAD_FOLDER = 'static/faction_logos'
    
    # Supabase Storage (for persistent file uploads)
    SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
    SUPABASE_STORAGE_BUCKET = 'faction-logos'
    
    # Application
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    # Inherit SQLALCHEMY_DATABASE_URI from Config (respects DATABASE_URL if set)


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
