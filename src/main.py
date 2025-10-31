import os
import sys
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from dotenv import load_dotenv
from src.config import DevelopmentConfig, PreproductionConfig, ProductionConfig, TestingConfig, Config
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name
from src.cache_config import CacheConfig, RateLimitConfig, invalidate_cache_pattern

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "octa-music-secret")

app_env = os.getenv("APP_ENV", "development").lower()

if app_env == "production":
    app.config.from_object(ProductionConfig)
elif app_env == "preproduction":
    app.config.from_object(PreproductionConfig)
elif app_env == "testing":
    app.config.from_object(TestingConfig)
elif app_env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(Config)


def init_cache_and_limiter():
    """Initialize cache and limiter with proper fallback handling."""
    global cache, limiter
    
    # Initialize Flask-Caching
    cache = None
    try:
        from flask_caching import Cache
        # Use SimpleCache for testing or when Redis URL not set, RedisCache for production
        if app.config.get('TESTING') or not app.config.get("CACHE_REDIS_URL"):
            app.config["CACHE_TYPE"] = "SimpleCache"
            cache = Cache(app)
            logger.info("Flask-Caching initialized with SimpleCache")
        else:
            try:
                # Try Redis cache first with timeout settings
                app.config["CACHE_TYPE"] = "RedisCache"
                app.config["CACHE_REDIS_URL"] = app.config.get("CACHE_REDIS_URL")
                app.config["CACHE_OPTIONS"] = {
                    "socket_connect_timeout": 2,
                    "socket_timeout": 2
                }
                cache = Cache(app)
                # Test the cache connection with a short timeout
                test_key = "init_test_key"
                cache.set(test_key, "test_value", timeout=1)
                cache.get(test_key)
                cache.delete(test_key)
                logger.info("Flask-Caching initialized successfully with Redis")
            except Exception as redis_error:
                logger.warning(f"Redis cache initialization failed: {redis_error}. Falling back to SimpleCache.")
                # Fallback to SimpleCache if Redis is not available
                app.config["CACHE_TYPE"] = "SimpleCache"
                cache = Cache(app)
                logger.info("Flask-Caching initialized with SimpleCache fallback")
    except Exception as e:
        logger.warning(f"Flask-Caching initialization failed: {e}. Running without cache.")
        cache = None

    # Initialize Flask-Limiter
    limiter = None
    try:
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address
        
        # Use in-memory storage for testing or when Redis not available
        if app.config.get('TESTING') or not app.config.get("RATELIMIT_STORAGE_URL"):
            limiter = Limiter(
                app=app,
                key_func=get_remote_address,
                default_limits=[app.config.get("RATELIMIT_DEFAULT", "200 per day, 50 per hour")],
                storage_uri="memory://",
                enabled=app.config.get("RATELIMIT_ENABLED", True)
            )
            logger.info("Flask-Limiter initialized with in-memory storage")
        else:
            try:
                limiter = Limiter(
                    app=app,
                    key_func=get_remote_address,
                    default_limits=[app.config.get("RATELIMIT_DEFAULT", "200 per day, 50 per hour")],
                    storage_uri=app.config.get("RATELIMIT_STORAGE_URL"),
                    enabled=app.config.get("RATELIMIT_ENABLED", True),
                    storage_options={
                        "socket_connect_timeout": 2,
                        "socket_timeout": 2,
                        "socket_keepalive": True,
                        "socket_keepalive_options": {},
                        "retry_on_timeout": False
                    }
                )
                logger.info("Flask-Limiter initialized successfully with Redis")
            except Exception as redis_error:
                logger.warning(f"Redis limiter initialization failed: {redis_error}. Falling back to in-memory storage.")
                # Fallback to in-memory storage
                limiter = Limiter(
                    app=app,
                    key_func=get_remote_address,
                    default_limits=[app.config.get("RATELIMIT_DEFAULT", "200 per day, 50 per hour")],
                    storage_uri="memory://",
                    enabled=app.config.get("RATELIMIT_ENABLED", True)
                )
                logger.info("Flask-Limiter initialized with in-memory storage fallback")
    except Exception as e:
        logger.warning(f"Flask-Limiter initialization failed: {e}. Running without rate limiting.")
        limiter = None
    
    return cache, limiter


# Try to initialize cache and limiter
# In case of import for testing, this might fail and will be retried when TESTING is set
cache, limiter = None, None
try:
    cache, limiter = init_cache_and_limiter()
except Exception as e:
    logger.warning(f"Initial cache/limiter initialization failed: {e}. Will use fallback mode.")

# Initialize services with cache support
spotify_service = SpotifyService(cache_instance=cache)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY")


@app.before_request
def ensure_initialized():
    """Ensure cache and limiter are initialized before first request."""
    global cache, limiter, spotify_service
    
    # Re-initialize if TESTING mode and not yet initialized properly
    if app.config.get('TESTING') and (cache is None or limiter is None):
        cache, limiter = init_cache_and_limiter()
        # Update spotify service with cache
        spotify_service.cache = cache


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "spotify":
            artist_name = request.form.get("artist_name")
            if artist_name:
                try:
                    artist = spotify_service.search_artist(artist_name)
                    if artist:
                        session['artist'] = artist
                        flash(f'Found artist: {artist["name"]}', 'success')
                    else:
                        session['artist'] = None
                        flash(f'No artist found for "{artist_name}". Please try another search.', 'error')
                except Exception as e:
                    logger.error(f"Spotify search error: {e}")
                    session['artist'] = None
                    flash('An error occurred while searching Spotify. Please try again.', 'error')
        elif action == "youtube":
            channel_name = request.form.get("channel_name")
            if channel_name:
                try:
                    yt_stats = get_channel_stats_by_name(channel_name, YOUTUBE_API_KEY, cache_instance=cache)
                    if yt_stats:
                        session['yt_stats'] = yt_stats
                        flash(f'Found channel: {yt_stats["title"]}', 'success')
                    else:
                        session['yt_stats'] = None
                        flash(f'No channel found for "{channel_name}". Please try another search.', 'error')
                except Exception as e:
                    logger.error(f"YouTube search error: {e}")
                    session['yt_stats'] = None
                    flash('An error occurred while searching YouTube. Please try again.', 'error')
        elif action == "clear":
            session.pop('artist', None)
            session.pop('yt_stats', None)
            flash('Search results cleared.', 'info')
        return redirect(url_for('home'))
    artist = session.get('artist')
    yt_stats = session.get('yt_stats')
    return render_template(
        "spotify.html",
        artist=artist,
        yt_stats=yt_stats
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for('home'))
    return render_template("login.html")


# Cache management endpoints
@app.route("/api/cache/clear", methods=["POST"])
def clear_cache():
    """Clear all cache entries."""
    try:
        if cache:
            cache.clear()
            logger.info("Cache cleared successfully")
            return jsonify({"status": "success", "message": "Cache cleared successfully"}), 200
        return jsonify({"status": "error", "message": "Cache not enabled"}), 400
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/cache/invalidate/<pattern>", methods=["POST"])
def invalidate_cache(pattern):
    """
    Invalidate cache entries matching a pattern.
    
    Examples:
    - /api/cache/invalidate/spotify:* - Clear all Spotify cache
    - /api/cache/invalidate/youtube:* - Clear all YouTube cache
    """
    try:
        if cache:
            count = invalidate_cache_pattern(cache, pattern)
            logger.info(f"Invalidated {count} cache entries matching pattern: {pattern}")
            return jsonify({
                "status": "success",
                "message": f"Invalidated {count} cache entries",
                "pattern": pattern
            }), 200
        return jsonify({"status": "error", "message": "Cache not enabled"}), 400
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint with cache and rate limiter status."""
    status = {
        "status": "healthy",
        "cache_enabled": cache is not None,
        "rate_limiter_enabled": limiter is not None,
        "environment": app_env
    }
    
    # Check cache connectivity
    if cache:
        try:
            cache.set("health_check", "ok", timeout=10)
            cache_value = cache.get("health_check")
            status["cache_status"] = "operational" if cache_value == "ok" else "degraded"
        except Exception as e:
            status["cache_status"] = f"error: {str(e)}"
            logger.error(f"Cache health check failed: {e}")
    
    return jsonify(status), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded errors."""
    logger.warning(f"Rate limit exceeded: {request.remote_addr}")
    return jsonify({
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later."
    }), 429


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
