"""
Redis cache configuration and utilities for API caching and rate limiting.
"""
import os
import logging
from functools import wraps
from typing import Optional, Callable, Any
import json
import hashlib

logger = logging.getLogger(__name__)


class CacheConfig:
    """Configuration for Redis cache"""
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TYPE = "RedisCache"
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))  # 5 minutes
    CACHE_KEY_PREFIX = "octa_music:"
    
    # Cache timeouts for different data types (in seconds)
    SPOTIFY_ARTIST_CACHE_TIMEOUT = int(os.getenv("SPOTIFY_CACHE_TIMEOUT", "3600"))  # 1 hour
    YOUTUBE_CHANNEL_CACHE_TIMEOUT = int(os.getenv("YOUTUBE_CACHE_TIMEOUT", "3600"))  # 1 hour
    YOUTUBE_VIDEO_CACHE_TIMEOUT = int(os.getenv("YOUTUBE_VIDEO_CACHE_TIMEOUT", "1800"))  # 30 minutes


class RateLimitConfig:
    """Configuration for rate limiting"""
    RATELIMIT_STORAGE_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day, 50 per hour")
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "True").lower() == "true"
    
    # API-specific rate limits
    SPOTIFY_RATE_LIMIT = os.getenv("SPOTIFY_RATE_LIMIT", "10 per minute")
    YOUTUBE_RATE_LIMIT = os.getenv("YOUTUBE_RATE_LIMIT", "10 per minute")


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key based on function arguments.
    
    Args:
        prefix: Prefix for the cache key
        *args: Positional arguments
        **kwargs: Keyword arguments
    
    Returns:
        A unique cache key string
    """
    # Create a string representation of all arguments
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
    key_str = ":".join(key_parts)
    
    # Hash the key if it's too long
    if len(key_str) > 200:
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{CacheConfig.CACHE_KEY_PREFIX}{prefix}:{key_hash}"
    
    return f"{CacheConfig.CACHE_KEY_PREFIX}{prefix}:{key_str}"


def cache_result(cache_instance, timeout: int, key_prefix: str):
    """
    Decorator to cache function results in Redis.
    
    Args:
        cache_instance: Flask-Caching cache instance
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
    
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            cache_key = generate_cache_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            try:
                cached_value = cache_instance.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return cached_value
            except Exception as e:
                logger.warning(f"Cache get error for key {cache_key}: {e}")
            
            # Call the function if not cached
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            if result is not None:
                try:
                    cache_instance.set(cache_key, result, timeout=timeout)
                    logger.debug(f"Cached result for key: {cache_key}")
                except Exception as e:
                    logger.warning(f"Cache set error for key {cache_key}: {e}")
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(cache_instance, pattern: str) -> int:
    """
    Invalidate all cache entries matching a pattern.
    
    Args:
        cache_instance: Flask-Caching cache instance
        pattern: Pattern to match cache keys (e.g., "spotify:*")
    
    Returns:
        Number of keys deleted
    """
    try:
        full_pattern = f"{CacheConfig.CACHE_KEY_PREFIX}{pattern}"
        
        # Get Redis client from cache instance
        if hasattr(cache_instance.cache, '_write_client'):
            redis_client = cache_instance.cache._write_client
        elif hasattr(cache_instance.cache, '_client'):
            redis_client = cache_instance.cache._client
        else:
            logger.error("Could not access Redis client from cache instance")
            return 0
        
        # Find all keys matching pattern
        keys = list(redis_client.scan_iter(match=full_pattern))
        if keys:
            deleted = redis_client.delete(*keys)
            logger.info(f"Invalidated {deleted} cache entries matching pattern: {full_pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return 0
