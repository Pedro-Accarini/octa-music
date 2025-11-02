import os

class Config:
    DEBUG = False
    TESTING = False
    
    # Spotify API
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    
    # SQLAlchemy (for playlists)
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///octa_music.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MongoDB (for authentication)
    MONGODB_URI = os.getenv('MONGODB_URI')
    MONGODB_DB_NAME = 'octa_music'
    
    # Flask-Mail Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Session Configuration
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    PERMANENT_SESSION_LIFETIME = int(os.getenv('PERMANENT_SESSION_LIFETIME', 4800))  # 80 minutes
    REMEMBER_ME_DURATION = int(os.getenv('REMEMBER_ME_DURATION', 2592000))  # 30 days
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    LOGIN_RATE_LIMIT_PER_MINUTE = int(os.getenv('LOGIN_RATE_LIMIT_PER_MINUTE', 3))
    LOGIN_RATE_LIMIT_PER_HOUR = int(os.getenv('LOGIN_RATE_LIMIT_PER_HOUR', 10))
    
    # Application URLs
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5000')
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None

class DevelopmentConfig(Config):
    DEBUG = True
    # In development, print emails to console instead of sending
    MAIL_SUPPRESS_SEND = os.getenv('MAIL_SUPPRESS_SEND', 'True').lower() == 'true'

class PreproductionConfig(Config):
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False
    # Force secure cookies in production
    SESSION_COOKIE_SECURE = True
