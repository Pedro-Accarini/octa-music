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

@patch('src.main.sp')
def test_home_get(mock_sp, client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'artist' in response.data or b'Artist' in response.data

@patch('src.main.sp')
def test_home_post_artist_found(mock_sp, client):
    mock_sp.search.return_value = {
        'artists': {
            'items': [{
                'name': 'Test Artist',
                'followers': {'total': 12345},
                'popularity': 80,
                'images': [{'url': 'http://example.com/image.jpg'}]
            }]
        }
    }
    response = client.post('/', data={'artist_name': 'Test Artist'})
    assert response.status_code == 200
    assert b'Test Artist' in response.data

@patch('src.main.sp')
def test_home_post_artist_not_found(mock_sp, client):
    mock_sp.search.return_value = {'artists': {'items': []}}
    response = client.post('/', data={'artist_name': 'Unknown Artist'})
    assert response.status_code == 200
    assert b'Unknown Artist' not in response.data
