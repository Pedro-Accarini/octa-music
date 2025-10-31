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
from src.models import db, Playlist, PlaylistSong

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

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()

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

# Playlist Routes
@app.route("/playlists")
def playlists():
    """Display all playlists"""
    all_playlists = Playlist.query.order_by(Playlist.created_at.desc()).all()
    return render_template("playlists.html", playlists=all_playlists)

@app.route("/playlists/create", methods=["GET", "POST"])
def create_playlist():
    """Create a new playlist"""
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        
        if not name:
            flash("Playlist name is required", "error")
            return redirect(url_for("create_playlist"))
        
        playlist = Playlist(name=name, description=description)
        db.session.add(playlist)
        db.session.commit()
        
        flash(f'Playlist "{name}" created successfully!', "success")
        return redirect(url_for("playlists"))
    
    return render_template("create_playlist.html")

@app.route("/playlists/<int:playlist_id>")
def view_playlist(playlist_id):
    """View a specific playlist with its songs"""
    playlist = Playlist.query.get_or_404(playlist_id)
    return render_template("view_playlist.html", playlist=playlist)

@app.route("/playlists/<int:playlist_id>/edit", methods=["GET", "POST"])
def edit_playlist(playlist_id):
    """Edit playlist details"""
    playlist = Playlist.query.get_or_404(playlist_id)
    
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        if not name:
            flash("Playlist name is required", "error")
            return redirect(url_for("edit_playlist", playlist_id=playlist_id))
        playlist.name = name
        playlist.description = description
        db.session.commit()
        
        flash(f'Playlist "{playlist.name}" updated successfully!', "success")
        return redirect(url_for("view_playlist", playlist_id=playlist_id))
    return render_template("edit_playlist.html", playlist=playlist)

@app.route("/playlists/<int:playlist_id>/delete", methods=["POST"])
def delete_playlist(playlist_id):
    """Delete a playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    playlist_name = playlist.name
    
    db.session.delete(playlist)
    db.session.commit()
    
    flash(f'Playlist "{playlist_name}" deleted successfully!', "success")
    return redirect(url_for("playlists"))

@app.route("/playlists/<int:playlist_id>/search", methods=["GET"])
def search_songs(playlist_id):
    """Search for songs to add to playlist"""
    playlist = Playlist.query.get_or_404(playlist_id)
    query = request.args.get("q", "")
    
    tracks = []
    if query:
        tracks = spotify_service.search_tracks(query, limit=20)
    
    return render_template("search_songs.html", playlist=playlist, tracks=tracks, query=query)

@app.route("/playlists/<int:playlist_id>/add_song", methods=["POST"])
def add_song_to_playlist(playlist_id):
    """Add a song to a playlist"""
    Playlist.query.get_or_404(playlist_id)
    
    track_id = request.form.get("track_id")
    track_name = request.form.get("track_name")
    artist_name = request.form.get("artist_name")
    album_name = request.form.get("album_name")
    duration_ms = request.form.get("duration_ms")
    image_url = request.form.get("image_url")
    spotify_url = request.form.get("spotify_url")
    
    # Check if song already exists in playlist
    existing = PlaylistSong.query.filter_by(
        playlist_id=playlist_id,
        spotify_track_id=track_id
    ).first()
    
    if existing:
        flash(f'"{track_name}" is already in this playlist!', "warning")
    else:
        try:
            duration = int(duration_ms) if duration_ms else None
        except (ValueError, TypeError):
            duration = None
        
        song = PlaylistSong(
            playlist_id=playlist_id,
            spotify_track_id=track_id,
            track_name=track_name,
            artist_name=artist_name,
            album_name=album_name,
            duration_ms=duration,
            image_url=image_url,
            spotify_url=spotify_url
        )
        db.session.add(song)
        db.session.commit()
        flash(f'"{track_name}" added to playlist!', "success")
    
    return redirect(url_for("view_playlist", playlist_id=playlist_id))

@app.route("/playlists/<int:playlist_id>/remove_song/<int:song_id>", methods=["POST"])
def remove_song_from_playlist(playlist_id, song_id):
    """Remove a song from a playlist"""
    song = PlaylistSong.query.filter_by(id=song_id, playlist_id=playlist_id).first_or_404()
    song_name = song.track_name
    
    db.session.delete(song)
    db.session.commit()
    
    flash(f'"{song_name}" removed from playlist!', "success")
    return redirect(url_for("view_playlist", playlist_id=playlist_id))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
