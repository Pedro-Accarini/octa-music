import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
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

@app.route("/search", methods=["GET"])
def search_page():
    """Advanced search page"""
    return render_template("search.html")

@app.route("/api/search", methods=["GET"])
def api_search():
    """API endpoint for advanced search"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'track,artist,album')
    limit = min(int(request.args.get('limit', 10)), 50)
    offset = int(request.args.get('offset', 0))
    sort_by = request.args.get('sort', 'relevance')
    
    if not query:
        return jsonify({'error': 'Query parameter is required'}), 400
    
    try:
        results = spotify_service.advanced_search(query, search_type, limit, offset)
        
        # Apply sorting if requested
        if sort_by == 'popularity':
            for key in ['tracks', 'artists', 'albums']:
                if key in results:
                    results[key] = sorted(results[key], key=lambda x: x.get('popularity', 0), reverse=True)
        elif sort_by == 'name':
            for key in ['tracks', 'artists', 'albums']:
                if key in results:
                    results[key] = sorted(results[key], key=lambda x: x.get('name', '').lower())
        
        # Store search in history (session-based)
        if 'search_history' not in session:
            session['search_history'] = []
        
        # Add to history if not duplicate of last search
        if not session['search_history'] or session['search_history'][0] != query:
            session['search_history'].insert(0, query)
            session['search_history'] = session['search_history'][:10]  # Keep last 10 searches
        
        session.modified = True
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/autocomplete", methods=["GET"])
def api_autocomplete():
    """API endpoint for autocomplete suggestions"""
    query = request.args.get('q', '')
    limit = min(int(request.args.get('limit', 5)), 10)
    
    if len(query) < 2:
        return jsonify([])
    
    try:
        suggestions = spotify_service.get_autocomplete_suggestions(query, limit)
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/search-history", methods=["GET", "DELETE"])
def api_search_history():
    """API endpoint for search history"""
    if request.method == "DELETE":
        session['search_history'] = []
        session.modified = True
        return jsonify({'success': True})
    
    return jsonify(session.get('search_history', []))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
