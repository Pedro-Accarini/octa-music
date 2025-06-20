import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for
from dotenv import load_dotenv
from src.config import DevelopmentConfig, PreproductionConfig, ProductionConfig, Config
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "octa-music-secret")

app_env = os.getenv("APP_ENV", "development").lower()

if app_env == "production":
    app.config.from_object(ProductionConfig)
elif app_env == "preproduction":
    app.config.from_object(PreproductionConfig)
elif app_env == "development":
    app.config.from_object(DevelopmentConfig)
else:
    app.config.from_object(Config)

spotify_service = SpotifyService()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "YOUR_API_KEY")

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "spotify":
            artist_name = request.form.get("artist_name")
            if artist_name:
                artist = spotify_service.search_artist(artist_name)
                session['artist'] = artist
        elif action == "youtube":
            channel_name = request.form.get("channel_name")
            if channel_name:
                yt_stats = get_channel_stats_by_name(channel_name, YOUTUBE_API_KEY)
                session['yt_stats'] = yt_stats
        return redirect(url_for('home'))
    artist = session.get('artist')
    yt_stats = session.get('yt_stats')
    return render_template(
        "spotify.html",
        artist=artist,
        yt_stats=yt_stats
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
