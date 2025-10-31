import os
import sys
import pytest
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

try:
    from src.main import app
    from src.services.spotify_service import SpotifyService
except Exception as e:
    print("Import error in test_advanced_search.py:", e)
    raise

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        yield client

def test_search_page_get(client):
    """Test that the advanced search page loads"""
    response = client.get('/search')
    assert response.status_code == 200
    assert b'Advanced Search' in response.data

@patch('src.main.spotify_service.advanced_search')
def test_api_search_endpoint(mock_advanced_search, client):
    """Test the API search endpoint"""
    mock_advanced_search.return_value = {
        'tracks': [{
            'id': '123',
            'name': 'Test Track',
            'artists': 'Test Artist',
            'album': 'Test Album',
            'duration_ms': 180000,
            'popularity': 80,
            'image_url': 'http://example.com/image.jpg',
            'spotify_url': 'http://spotify.com/track/123',
            'preview_url': 'http://example.com/preview.mp3',
            'type': 'track'
        }],
        'artists': [],
        'albums': []
    }
    
    response = client.get('/api/search?q=test')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'tracks' in data
    assert len(data['tracks']) == 1
    assert data['tracks'][0]['name'] == 'Test Track'

def test_api_search_no_query(client):
    """Test API search endpoint without query parameter"""
    response = client.get('/api/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('src.main.spotify_service.get_autocomplete_suggestions')
def test_api_autocomplete_endpoint(mock_autocomplete, client):
    """Test the autocomplete API endpoint"""
    mock_autocomplete.return_value = ['Artist One', 'Artist Two']
    
    response = client.get('/api/autocomplete?q=art')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert 'Artist One' in data

def test_api_autocomplete_short_query(client):
    """Test autocomplete with short query returns empty list"""
    response = client.get('/api/autocomplete?q=a')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 0

def test_search_history_get(client):
    """Test getting search history"""
    with client.session_transaction() as sess:
        sess['search_history'] = ['query1', 'query2']
    
    response = client.get('/api/search-history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert 'query1' in data

def test_search_history_delete(client):
    """Test clearing search history"""
    with client.session_transaction() as sess:
        sess['search_history'] = ['query1', 'query2']
    
    response = client.delete('/api/search-history')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True

@patch('src.main.spotify_service.advanced_search')
def test_search_sorting_by_popularity(mock_advanced_search, client):
    """Test that search results can be sorted by popularity"""
    mock_advanced_search.return_value = {
        'tracks': [
            {'name': 'Track A', 'popularity': 50},
            {'name': 'Track B', 'popularity': 80},
            {'name': 'Track C', 'popularity': 60}
        ],
        'artists': [],
        'albums': []
    }
    
    response = client.get('/api/search?q=test&sort=popularity')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that results are sorted by popularity (descending)
    assert data['tracks'][0]['popularity'] == 80
    assert data['tracks'][1]['popularity'] == 60
    assert data['tracks'][2]['popularity'] == 50

@patch('src.main.spotify_service.advanced_search')
def test_search_sorting_by_name(mock_advanced_search, client):
    """Test that search results can be sorted by name"""
    mock_advanced_search.return_value = {
        'tracks': [],
        'artists': [
            {'name': 'Zebra Artist', 'popularity': 50},
            {'name': 'Apple Artist', 'popularity': 80},
            {'name': 'Middle Artist', 'popularity': 60}
        ],
        'albums': []
    }
    
    response = client.get('/api/search?q=test&sort=name')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that results are sorted by name (ascending)
    assert data['artists'][0]['name'] == 'Apple Artist'
    assert data['artists'][1]['name'] == 'Middle Artist'
    assert data['artists'][2]['name'] == 'Zebra Artist'

@patch('src.main.spotify_service.advanced_search')
def test_search_with_type_filter(mock_advanced_search, client):
    """Test search with specific type filter"""
    mock_advanced_search.return_value = {
        'tracks': [{'name': 'Test Track'}],
        'artists': [],
        'albums': []
    }
    
    response = client.get('/api/search?q=test&type=track')
    assert response.status_code == 200
    mock_advanced_search.assert_called_once()
    call_args = mock_advanced_search.call_args
    assert call_args[0][1] == 'track'  # search_type argument
