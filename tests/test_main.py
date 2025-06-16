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
    response = client.post('/', data={'artist_name': 'Test Artist'})
    assert response.status_code == 200
    assert b'Test Artist' in response.data

@patch('src.main.spotify_service.search_artist')
def test_home_post_artist_not_found(mock_search_artist, client):
    mock_search_artist.return_value = None
    response = client.post('/', data={'artist_name': 'Nonexistent Artist'})
    assert response.status_code == 200
    assert b'artist' in response.data or b'Artist' in response.data
