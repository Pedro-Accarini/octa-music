import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

from src.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['status'] == 'healthy'

@patch('src.api.routes.spotify_service.search_artist')
def test_spotify_search_success(mock_search, client):
    """Test successful Spotify artist search."""
    mock_search.return_value = {
        'name': 'Test Artist',
        'followers': '12,345',
        'popularity': 80,
        'image_url': 'http://example.com/image.jpg',
        'genres': 'pop',
        'spotify_url': 'http://spotify.com/artist/123',
    }
    
    response = client.post('/api/v1/spotify/search', 
                          json={'artist_name': 'Test Artist'},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['name'] == 'Test Artist'
    assert data['message'] == 'Artist found successfully'

@patch('src.api.routes.spotify_service.search_artist')
def test_spotify_search_not_found(mock_search, client):
    """Test Spotify artist not found."""
    mock_search.return_value = None
    
    response = client.post('/api/v1/spotify/search', 
                          json={'artist_name': 'Unknown Artist'},
                          content_type='application/json')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'not found' in data['error'].lower()

def test_spotify_search_missing_name(client):
    """Test Spotify search with missing artist_name."""
    response = client.post('/api/v1/spotify/search', 
                          json={},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'required' in data['error'].lower()

def test_spotify_search_invalid_content_type(client):
    """Test Spotify search with invalid content type."""
    response = client.post('/api/v1/spotify/search', 
                          data='artist_name=Test')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'application/json' in data['error']

@patch('src.api.routes.get_channel_stats_by_name')
def test_youtube_search_success(mock_search, client):
    """Test successful YouTube channel search."""
    mock_search.return_value = {
        'title': 'Test Channel',
        'subscribers': '1000',
        'views': '50000',
        'video_count': 10,
        'channel_url': 'http://youtube.com/channel/abc',
    }
    
    response = client.post('/api/v1/youtube/search', 
                          json={'channel_name': 'Test Channel'},
                          content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['data']['title'] == 'Test Channel'
    assert data['message'] == 'Channel found successfully'

@patch('src.api.routes.get_channel_stats_by_name')
def test_youtube_search_not_found(mock_search, client):
    """Test YouTube channel not found."""
    mock_search.return_value = None
    
    response = client.post('/api/v1/youtube/search', 
                          json={'channel_name': 'Unknown Channel'},
                          content_type='application/json')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'not found' in data['error'].lower()

def test_youtube_search_too_long_name(client):
    """Test YouTube search with too long channel name."""
    long_name = 'A' * 101
    response = client.post('/api/v1/youtube/search', 
                          json={'channel_name': long_name},
                          content_type='application/json')
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'less than 100' in data['error']
