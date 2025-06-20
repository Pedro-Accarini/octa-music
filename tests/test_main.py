import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

try:
    from src.main import app
except Exception as e:
    print("Import error in test_main.py:", e)
    raise

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

@patch('src.main.spotify_service.search_artist')
def test_home_get(mock_search_artist, client):
    mock_search_artist.return_value = None
    response = client.get('/')
    assert response.status_code == 200
    assert b'artist' in response.data or b'Artist' in response.data

@patch('src.main.spotify_service.search_artist')
def test_home_post_artist_found(mock_search_artist, client):
    mock_search_artist.return_value = {
        'name': 'Test Artist',
        'followers': '12,345',
        'popularity': 80,
        'image_url': 'http://example.com/image.jpg',
        'genres': 'pop',
        'spotify_url': 'http://spotify.com/artist/123',
    }
    response = client.post('/', data={'artist_name': 'Test Artist', 'action': 'spotify'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Artist' in response.data

@patch('src.main.spotify_service.search_artist')
def test_home_post_artist_not_found(mock_search_artist, client):
    mock_search_artist.return_value = None
    response = client.post('/', data={'artist_name': 'Nonexistent Artist'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'artist' in response.data or b'Artist' in response.data

@patch('src.main.get_channel_stats_by_name')
def test_home_post_youtube_found(mock_get_channel_stats, client):
    mock_get_channel_stats.return_value = {
        'title': 'Test Channel',
        'subscribers': '1000',
        'views': '50000',
        'video_count': 10,
        'thumbnail_url': 'http://example.com/thumb.jpg',
        'channel_url': 'http://youtube.com/channel/abc',
    }
    response = client.post('/', data={'channel_name': 'Test Channel', 'action': 'youtube'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Test Channel' in response.data
