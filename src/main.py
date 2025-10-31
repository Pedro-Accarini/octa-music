import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for, flash
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
                try:
                    artist = spotify_service.search_artist(artist_name)
                    if artist:
                        session['artist'] = artist
                        flash(f'Found artist: {artist["name"]}', 'success')
                    else:
                        session['artist'] = None
                        flash(f'No artist found for "{artist_name}". Please try another search.', 'error')
                except Exception as e:
                    session['artist'] = None
                    flash('An error occurred while searching Spotify. Please try again.', 'error')
        elif action == "youtube":
            channel_name = request.form.get("channel_name")
            if channel_name:
                try:
                    yt_stats = get_channel_stats_by_name(channel_name, YOUTUBE_API_KEY)
                    if yt_stats:
                        session['yt_stats'] = yt_stats
                        flash(f'Found channel: {yt_stats["title"]}', 'success')
                    else:
                        session['yt_stats'] = None
                        flash(f'No channel found for "{channel_name}". Please try another search.', 'error')
                except Exception as e:
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
