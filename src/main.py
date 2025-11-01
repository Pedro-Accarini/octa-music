import os
import sys
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from src.config import DevelopmentConfig, PreproductionConfig, ProductionConfig, Config
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name
from src.api.routes import api_bp

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "octa-music-secret")

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Configure rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

app_env = os.getenv("APP_ENV", "development").lower()

if app_env == "production":
    app.config.from_object(ProductionConfig)
elif app_env == "preproduction":
    app.config.from_object(PreproductionConfig)
elif app_env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(Config)

# Register API blueprint
app.register_blueprint(api_bp)

try:
    spotify_service = SpotifyService()
except ValueError as e:
    logger.warning(f"Failed to initialize Spotify service: {e}")
    spotify_service = None

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY")

@app.route("/", methods=["GET", "POST"])
@limiter.limit("30 per minute")
def home():
    error_message = None
    success_message = None
    
    if request.method == "POST":
        action = request.form.get("action")
        
        if action == "spotify":
            artist_name = request.form.get("artist_name", "").strip()
            if artist_name:
                if not spotify_service:
                    error_message = "Spotify service is not configured"
                    session['error'] = error_message
                else:
                    try:
                        artist = spotify_service.search_artist(artist_name)
                        if artist:
                            session['artist'] = artist
                            success_message = f"Found artist: {artist['name']}"
                            session['success'] = success_message
                        else:
                            error_message = f"No artist found for '{artist_name}'"
                            session['error'] = error_message
                    except Exception as e:
                        logger.error(f"Error searching artist: {e}")
                        error_message = "An error occurred while searching for the artist"
                        session['error'] = error_message
            else:
                error_message = "Please enter an artist name"
                session['error'] = error_message
                
        elif action == "youtube":
            channel_name = request.form.get("channel_name", "").strip()
            if channel_name:
                try:
                    yt_stats = get_channel_stats_by_name(channel_name, YOUTUBE_API_KEY)
                    if yt_stats:
                        session['yt_stats'] = yt_stats
                        success_message = f"Found channel: {yt_stats['title']}"
                        session['success'] = success_message
                    else:
                        error_message = f"No channel found for '{channel_name}'"
                        session['error'] = error_message
                except Exception as e:
                    logger.error(f"Error searching channel: {e}")
                    error_message = "An error occurred while searching for the channel"
                    session['error'] = error_message
            else:
                error_message = "Please enter a channel name"
                session['error'] = error_message
                
        return redirect(url_for('home'))
    
    # Get messages from session and clear them
    error_message = session.pop('error', None)
    success_message = session.pop('success', None)
    artist = session.get('artist')
    yt_stats = session.get('yt_stats')
    
    return render_template(
        "spotify.html",
        artist=artist,
        yt_stats=yt_stats,
        error_message=error_message,
        success_message=success_message
    )

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template("spotify.html", error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}")
    return render_template("spotify.html", error_message="An internal error occurred"), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit errors."""
    return render_template("spotify.html", error_message="Rate limit exceeded. Please try again later."), 429

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
