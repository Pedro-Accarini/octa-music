import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

from src.main import app, db
from src.models import Playlist, PlaylistSong

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SECRET_KEY'] = 'test_secret_key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_playlists_page_empty(client):
    """Test playlists page when no playlists exist"""
    response = client.get('/playlists')
    assert response.status_code == 200
    assert b"don't have any playlists" in response.data

def test_create_playlist(client):
    """Test creating a new playlist"""
    response = client.post('/playlists/create', data={
        'name': 'My Test Playlist',
        'description': 'A test playlist'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'My Test Playlist' in response.data
    assert b'created successfully' in response.data

def test_create_playlist_without_name(client):
    """Test creating playlist without a name"""
    response = client.post('/playlists/create', data={
        'description': 'A test playlist'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'required' in response.data

def test_view_playlist(client):
    """Test viewing a specific playlist"""
    # Create a playlist first
    with app.app_context():
        playlist = Playlist(name='Test Playlist', description='Test Description')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    response = client.get(f'/playlists/{playlist_id}')
    assert response.status_code == 200
    assert b'Test Playlist' in response.data
    assert b'Test Description' in response.data

def test_edit_playlist(client):
    """Test editing a playlist"""
    # Create a playlist first
    with app.app_context():
        playlist = Playlist(name='Original Name', description='Original Description')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    response = client.post(f'/playlists/{playlist_id}/edit', data={
        'name': 'Updated Name',
        'description': 'Updated Description'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Updated Name' in response.data
    assert b'updated successfully' in response.data

def test_delete_playlist(client):
    """Test deleting a playlist"""
    # Create a playlist first
    with app.app_context():
        playlist = Playlist(name='To Delete', description='Will be deleted')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    response = client.post(f'/playlists/{playlist_id}/delete', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'deleted successfully' in response.data

@patch('src.main.spotify_service.search_tracks')
def test_search_songs(mock_search_tracks, client):
    """Test searching for songs to add to playlist"""
    # Create a playlist first
    with app.app_context():
        playlist = Playlist(name='Test Playlist')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    mock_search_tracks.return_value = [{
        'id': 'track123',
        'name': 'Test Song',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'duration_ms': 180000,
        'image_url': 'http://example.com/image.jpg',
        'spotify_url': 'http://spotify.com/track/123',
        'preview_url': None
    }]
    
    response = client.get(f'/playlists/{playlist_id}/search?q=test')
    assert response.status_code == 200
    assert b'Test Song' in response.data
    assert b'Test Artist' in response.data

def test_add_song_to_playlist(client):
    """Test adding a song to a playlist"""
    # Create a playlist first
    with app.app_context():
        playlist = Playlist(name='Test Playlist')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    response = client.post(f'/playlists/{playlist_id}/add_song', data={
        'track_id': 'track123',
        'track_name': 'Test Song',
        'artist_name': 'Test Artist',
        'album_name': 'Test Album',
        'duration_ms': '180000',
        'image_url': 'http://example.com/image.jpg',
        'spotify_url': 'http://spotify.com/track/123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Test Song' in response.data
    assert b'added to playlist' in response.data

def test_add_duplicate_song_to_playlist(client):
    """Test adding the same song twice to a playlist"""
    # Create a playlist and add a song
    with app.app_context():
        playlist = Playlist(name='Test Playlist')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
        
        song = PlaylistSong(
            playlist_id=playlist_id,
            spotify_track_id='track123',
            track_name='Test Song',
            artist_name='Test Artist'
        )
        db.session.add(song)
        db.session.commit()
    
    # Try to add the same song again
    response = client.post(f'/playlists/{playlist_id}/add_song', data={
        'track_id': 'track123',
        'track_name': 'Test Song',
        'artist_name': 'Test Artist',
        'album_name': 'Test Album',
        'duration_ms': '180000',
        'image_url': 'http://example.com/image.jpg',
        'spotify_url': 'http://spotify.com/track/123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'already in this playlist' in response.data

def test_remove_song_from_playlist(client):
    """Test removing a song from a playlist"""
    # Create a playlist and add a song
    with app.app_context():
        playlist = Playlist(name='Test Playlist')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
        
        song = PlaylistSong(
            playlist_id=playlist_id,
            spotify_track_id='track123',
            track_name='Test Song',
            artist_name='Test Artist'
        )
        db.session.add(song)
        db.session.commit()
        song_id = song.id
    
    response = client.post(f'/playlists/{playlist_id}/remove_song/{song_id}', follow_redirects=True)
    
    assert response.status_code == 200
    assert b'removed from playlist' in response.data

def test_playlist_not_found(client):
    """Test accessing a non-existent playlist"""
    response = client.get('/playlists/9999')
    assert response.status_code == 404

@patch('src.main.spotify_service.search_tracks')
def test_search_tracks_service(mock_search_tracks, client):
    """Test that SpotifyService.search_tracks is called correctly"""
    with app.app_context():
        playlist = Playlist(name='Test Playlist')
        db.session.add(playlist)
        db.session.commit()
        playlist_id = playlist.id
    
    mock_search_tracks.return_value = []
    
    client.get(f'/playlists/{playlist_id}/search?q=beatles')
    
    mock_search_tracks.assert_called_once_with('beatles', limit=20)
