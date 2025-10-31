import os

class Config:
    DEBUG = False
    TESTING = False
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    
    # Redis Cache Configuration
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_URL = os.getenv("REDIS_URL")  # No default, will use SimpleCache if not set
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))
    CACHE_KEY_PREFIX = "octa_music:"
    
    # Rate Limiting Configuration
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL")  # No default, will use in-memory if not set
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() == "true"
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day, 50 per hour")

class DevelopmentConfig(Config):
    DEBUG = True
    # More relaxed rate limits for development
    RATELIMIT_DEFAULT = "1000 per day, 200 per hour"
    # Use defaults for development if not set
    CACHE_REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    # No Redis for testing - will use in-memory/SimpleCache
    CACHE_TYPE = "SimpleCache"
    CACHE_REDIS_URL = None
    RATELIMIT_STORAGE_URL = None
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "10000 per day, 1000 per hour"

class PreproductionConfig(Config):
    DEBUG = False

class ProductionConfig(Config):
    DEBUG = False
