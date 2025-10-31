import os
import sys
import secrets
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from __init__ import __version__
except ImportError:
    __version__ = "unknown"

from flask import Flask, request, render_template, session, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
from src.config import DevelopmentConfig, PreproductionConfig, ProductionConfig, Config
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name
from src.models import db, User, Song, Like, Rating, Comment, Share, Activity

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

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            session['logged_in'] = True
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template("register.html")
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template("register.html")
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('logged_in', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))


@app.route("/profile")
@login_required
def profile():
    user_likes = Like.query.filter_by(user_id=current_user.id).order_by(Like.created_at.desc()).all()
    user_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(Rating.updated_at.desc()).all()
    user_comments = Comment.query.filter_by(user_id=current_user.id).order_by(Comment.created_at.desc()).all()
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.created_at.desc()).limit(20).all()
    
    return render_template("profile.html", 
                         likes=user_likes, 
                         ratings=user_ratings, 
                         comments=user_comments,
                         activities=activities)


# API endpoints for social features
@app.route("/api/song/like", methods=["POST"])
@login_required
def like_song():
    data = request.get_json()
    spotify_id = data.get('spotify_id')
    name = data.get('name')
    artist_name = data.get('artist_name')
    image_url = data.get('image_url')
    spotify_url = data.get('spotify_url')
    
    if not spotify_id or not name or not artist_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get or create song
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        song = Song(spotify_id=spotify_id, name=name, artist_name=artist_name, 
                   image_url=image_url, spotify_url=spotify_url)
        db.session.add(song)
        db.session.commit()
    
    # Check if already liked
    existing_like = Like.query.filter_by(user_id=current_user.id, song_id=song.id).first()
    if existing_like:
        return jsonify({'error': 'Song already liked'}), 400
    
    # Create like
    like = Like(user_id=current_user.id, song_id=song.id)
    db.session.add(like)
    
    # Create activity
    activity = Activity(user_id=current_user.id, song_id=song.id, 
                       activity_type='like', details=f'Liked {song.name}')
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'success': True, 'total_likes': song.total_likes})


@app.route("/api/song/unlike", methods=["POST"])
@login_required
def unlike_song():
    data = request.get_json()
    spotify_id = data.get('spotify_id')
    
    if not spotify_id:
        return jsonify({'error': 'Missing spotify_id'}), 400
    
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        return jsonify({'error': 'Song not found'}), 404
    
    like = Like.query.filter_by(user_id=current_user.id, song_id=song.id).first()
    if not like:
        return jsonify({'error': 'Song not liked'}), 400
    
    db.session.delete(like)
    db.session.commit()
    
    return jsonify({'success': True, 'total_likes': song.total_likes})


@app.route("/api/song/rate", methods=["POST"])
@login_required
def rate_song():
    data = request.get_json()
    spotify_id = data.get('spotify_id')
    rating_value = data.get('rating')
    name = data.get('name')
    artist_name = data.get('artist_name')
    image_url = data.get('image_url')
    spotify_url = data.get('spotify_url')
    
    if not spotify_id or rating_value is None or not name or not artist_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        rating_value = int(rating_value)
        if rating_value < 1 or rating_value > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid rating value'}), 400
    
    # Get or create song
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        song = Song(spotify_id=spotify_id, name=name, artist_name=artist_name,
                   image_url=image_url, spotify_url=spotify_url)
        db.session.add(song)
        db.session.commit()
    
    # Update or create rating
    existing_rating = Rating.query.filter_by(user_id=current_user.id, song_id=song.id).first()
    if existing_rating:
        existing_rating.rating = rating_value
    else:
        new_rating = Rating(user_id=current_user.id, song_id=song.id, rating=rating_value)
        db.session.add(new_rating)
        
        # Create activity only for new ratings
        activity = Activity(user_id=current_user.id, song_id=song.id,
                           activity_type='rating', details=f'Rated {song.name} {rating_value} stars')
        db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'success': True, 'average_rating': song.average_rating})


@app.route("/api/song/comment", methods=["POST"])
@login_required
def add_comment():
    data = request.get_json()
    spotify_id = data.get('spotify_id')
    content = data.get('content')
    name = data.get('name')
    artist_name = data.get('artist_name')
    image_url = data.get('image_url')
    spotify_url = data.get('spotify_url')
    
    if not spotify_id or not content or not name or not artist_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get or create song
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        song = Song(spotify_id=spotify_id, name=name, artist_name=artist_name,
                   image_url=image_url, spotify_url=spotify_url)
        db.session.add(song)
        db.session.commit()
    
    # Create comment
    comment = Comment(user_id=current_user.id, song_id=song.id, content=content)
    db.session.add(comment)
    
    # Create activity
    activity = Activity(user_id=current_user.id, song_id=song.id,
                       activity_type='comment', details=f'Commented on {song.name}')
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'comment': {
            'id': comment.id,
            'username': current_user.username,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@app.route("/api/song/comments/<spotify_id>", methods=["GET"])
def get_comments(spotify_id):
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        return jsonify({'comments': []})
    
    comments = Comment.query.filter_by(song_id=song.id).order_by(Comment.created_at.desc()).all()
    
    return jsonify({
        'comments': [{
            'id': c.id,
            'username': c.user.username,
            'content': c.content,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
        } for c in comments]
    })


@app.route("/api/song/share", methods=["POST"])
@login_required
def share_song():
    data = request.get_json()
    spotify_id = data.get('spotify_id')
    name = data.get('name')
    artist_name = data.get('artist_name')
    image_url = data.get('image_url')
    spotify_url = data.get('spotify_url')
    
    if not spotify_id or not name or not artist_name:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Get or create song
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    if not song:
        song = Song(spotify_id=spotify_id, name=name, artist_name=artist_name,
                   image_url=image_url, spotify_url=spotify_url)
        db.session.add(song)
        db.session.commit()
    
    # Generate unique share token
    share_token = secrets.token_urlsafe(16)
    
    # Create share
    share = Share(user_id=current_user.id, song_id=song.id, share_token=share_token)
    db.session.add(share)
    
    # Create activity
    activity = Activity(user_id=current_user.id, song_id=song.id,
                       activity_type='share', details=f'Shared {song.name}')
    db.session.add(activity)
    
    db.session.commit()
    
    share_url = url_for('view_shared_song', token=share_token, _external=True)
    
    return jsonify({'success': True, 'share_url': share_url})


@app.route("/shared/<token>")
def view_shared_song(token):
    share = Share.query.filter_by(share_token=token).first()
    if not share:
        flash('Shared song not found', 'error')
        return redirect(url_for('home'))
    
    song = share.song
    return render_template("shared_song.html", song=song, shared_by=share.user.username)


@app.route("/api/song/status/<spotify_id>")
def get_song_status(spotify_id):
    """Get like/rating status for current user"""
    song = Song.query.filter_by(spotify_id=spotify_id).first()
    
    response = {
        'total_likes': 0,
        'average_rating': 0,
        'user_liked': False,
        'user_rating': 0
    }
    
    if song:
        response['total_likes'] = song.total_likes
        response['average_rating'] = round(song.average_rating, 1)
        
        if current_user.is_authenticated:
            user_like = Like.query.filter_by(user_id=current_user.id, song_id=song.id).first()
            response['user_liked'] = user_like is not None
            
            user_rating = Rating.query.filter_by(user_id=current_user.id, song_id=song.id).first()
            response['user_rating'] = user_rating.rating if user_rating else 0
    
    return jsonify(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config["DEBUG"])
