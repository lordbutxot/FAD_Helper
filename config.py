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
    db_url = os.environ.get('DATABASE_URL')
    if db_url:
        # Production: PostgreSQL on Render
        # Convert postgres:// to postgresql:// (SQLAlchemy 1.4+ requires this)
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = db_url
    else:
        # Local development: SQLite
        SQLALCHEMY_DATABASE_URI = 'sqlite:///fad_lists.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    # Supabase requires SSL. Append to URL if needed.
    if db_url and 'supabase.co' in db_url and '?sslmode=' not in db_url:
        SQLALCHEMY_DATABASE_URI = db_url + '?sslmode=require'
    
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
    
    # Application
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # Allow HTTP in development
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fad_lists.db'


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
