import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

from src.main import app
from src.models import db, User, Song, Like, Rating, Comment, Share, Activity

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def test_user(client):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_song(client):
    """Create a test song"""
    with app.app_context():
        song = Song(
            spotify_id='test_spotify_id',
            name='Test Song',
            artist_name='Test Artist',
            image_url='http://example.com/image.jpg',
            spotify_url='http://spotify.com/track/123'
        )
        db.session.add(song)
        db.session.commit()
        return song

def login_user(client, username='testuser', password='password123'):
    """Helper function to log in a user"""
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

# Authentication Tests
def test_register_new_user(client):
    """Test user registration"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Registration successful' in response.data or b'Please log in' in response.data
    
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username"""
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'another@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_register_password_mismatch(client):
    """Test registration with mismatched passwords"""
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'confirm_password': 'different_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data

def test_login_success(client, test_user):
    """Test successful login"""
    response = login_user(client)
    assert response.status_code == 200
    assert b'Welcome back' in response.data or b'testuser' in response.data

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

def test_logout(client, test_user):
    """Test logout"""
    login_user(client)
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'logged out' in response.data

# Like Feature Tests
def test_like_song(client, test_user):
    """Test liking a song"""
    login_user(client)
    
    response = client.post('/api/song/like', 
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    
    with app.app_context():
        like = Like.query.first()
        assert like is not None
        assert like.song.spotify_id == 'test_spotify_123'

def test_unlike_song(client, test_user, test_song):
    """Test unliking a song"""
    login_user(client)
    
    # First like the song
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.filter_by(spotify_id='test_spotify_id').first()
        like = Like(user_id=user.id, song_id=song.id)
        db.session.add(like)
        db.session.commit()
    
    # Then unlike it
    response = client.post('/api/song/unlike',
        json={'spotify_id': 'test_spotify_id'})
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True

def test_like_requires_login(client):
    """Test that liking requires authentication"""
    response = client.post('/api/song/like',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist'
        })
    
    # Flask-Login redirects to login page when not authenticated
    assert response.status_code == 302

# Rating Feature Tests
def test_rate_song(client, test_user):
    """Test rating a song"""
    login_user(client)
    
    response = client.post('/api/song/rate',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'rating': 5,
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['average_rating'] == 5.0
    
    with app.app_context():
        rating = Rating.query.first()
        assert rating is not None
        assert rating.rating == 5

def test_rate_song_invalid_rating(client, test_user):
    """Test rating with invalid value"""
    login_user(client)
    
    response = client.post('/api/song/rate',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'rating': 6  # Invalid: should be 1-5
        })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_update_existing_rating(client, test_user, test_song):
    """Test updating an existing rating"""
    login_user(client)
    
    # Create initial rating
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.filter_by(spotify_id='test_spotify_id').first()
        rating = Rating(user_id=user.id, song_id=song.id, rating=3)
        db.session.add(rating)
        db.session.commit()
    
    # Update rating
    response = client.post('/api/song/rate',
        json={
            'spotify_id': 'test_spotify_id',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'rating': 5
        })
    
    assert response.status_code == 200
    
    with app.app_context():
        updated_rating = Rating.query.first()
        assert updated_rating.rating == 5

# Comment Feature Tests
def test_add_comment(client, test_user):
    """Test adding a comment"""
    login_user(client)
    
    response = client.post('/api/song/comment',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'content': 'Great song!',
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['comment']['content'] == 'Great song!'
    
    with app.app_context():
        comment = Comment.query.first()
        assert comment is not None
        assert comment.content == 'Great song!'

def test_get_comments(client, test_user, test_song):
    """Test retrieving comments for a song"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.filter_by(spotify_id='test_spotify_id').first()
        comment1 = Comment(user_id=user.id, song_id=song.id, content='First comment')
        comment2 = Comment(user_id=user.id, song_id=song.id, content='Second comment')
        db.session.add_all([comment1, comment2])
        db.session.commit()
    
    response = client.get('/api/song/comments/test_spotify_id')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['comments']) == 2

def test_add_comment_requires_login(client):
    """Test that commenting requires authentication"""
    response = client.post('/api/song/comment',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'content': 'Great song!'
        })
    
    # Flask-Login redirects to login page when not authenticated
    assert response.status_code == 302

# Share Feature Tests
def test_share_song(client, test_user):
    """Test sharing a song"""
    login_user(client)
    
    response = client.post('/api/song/share',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'share_url' in data
    
    with app.app_context():
        share = Share.query.first()
        assert share is not None
        assert share.song.spotify_id == 'test_spotify_123'

def test_view_shared_song(client, test_user, test_song):
    """Test viewing a shared song"""
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.filter_by(spotify_id='test_spotify_id').first()
        share = Share(user_id=user.id, song_id=song.id, share_token='test_token_123')
        db.session.add(share)
        db.session.commit()
    
    response = client.get('/shared/test_token_123')
    
    assert response.status_code == 200
    assert b'Test Song' in response.data

def test_view_invalid_shared_song(client):
    """Test viewing a non-existent shared song"""
    response = client.get('/shared/invalid_token', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'not found' in response.data

# Profile Tests
def test_profile_requires_login(client):
    """Test that profile page requires authentication"""
    response = client.get('/profile')
    assert response.status_code == 302  # Redirect to login

def test_profile_page(client, test_user):
    """Test accessing profile page when logged in"""
    login_user(client)
    response = client.get('/profile')
    
    assert response.status_code == 200
    assert b'testuser' in response.data

# Activity Feed Tests
def test_activity_created_on_like(client, test_user):
    """Test that activity is created when liking"""
    login_user(client)
    
    client.post('/api/song/like',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    with app.app_context():
        activity = Activity.query.filter_by(activity_type='like').first()
        assert activity is not None

def test_activity_created_on_rating(client, test_user):
    """Test that activity is created when rating"""
    login_user(client)
    
    client.post('/api/song/rate',
        json={
            'spotify_id': 'test_spotify_123',
            'name': 'Test Song',
            'artist_name': 'Test Artist',
            'rating': 5,
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123'
        })
    
    with app.app_context():
        activity = Activity.query.filter_by(activity_type='rating').first()
        assert activity is not None

# Song Status API Tests
def test_get_song_status_not_authenticated(client, test_song):
    """Test getting song status when not logged in"""
    response = client.get('/api/song/status/test_spotify_id')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['user_liked'] is False
    assert data['user_rating'] == 0

def test_get_song_status_authenticated(client, test_user, test_song):
    """Test getting song status when logged in with interactions"""
    login_user(client)
    
    # Create like and rating
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        song = Song.query.filter_by(spotify_id='test_spotify_id').first()
        like = Like(user_id=user.id, song_id=song.id)
        rating = Rating(user_id=user.id, song_id=song.id, rating=4)
        db.session.add_all([like, rating])
        db.session.commit()
    
    response = client.get('/api/song/status/test_spotify_id')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['user_liked'] is True
    assert data['user_rating'] == 4
