import os
import pytest
from unittest.mock import patch, MagicMock

from src.main import app


@pytest.fixture
def app_context():
    """Create an application context."""
    with app.app_context():
        yield


class TestHomeRoute:
    """Test cases for the home route."""

    @patch('src.main.spotify_service.search_artist')
    def test_home_get_request(self, mock_search_artist, client):
        """Test GET request to home page."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'artist' in response.data or b'Artist' in response.data

    @patch('src.main.spotify_service.search_artist')
    def test_home_post_spotify_artist_found(self, mock_search_artist, client):
        """Test POST request with valid artist name."""
        mock_search_artist.return_value = {
            'name': 'Test Artist',
            'followers': '12,345',
            'popularity': 80,
            'image_url': 'http://example.com/image.jpg',
            'genres': 'pop, rock',
            'spotify_url': 'http://spotify.com/artist/123',
        }
        
        response = client.post('/', data={
            'artist_name': 'Test Artist',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Test Artist' in response.data
        mock_search_artist.assert_called_once_with('Test Artist')

    @patch('src.main.spotify_service.search_artist')
    def test_home_post_spotify_artist_not_found(self, mock_search_artist, client):
        """Test POST request when artist is not found."""
        mock_search_artist.return_value = None
        
        response = client.post('/', data={
            'artist_name': 'Nonexistent Artist',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        mock_search_artist.assert_called_once_with('Nonexistent Artist')

    @patch('src.main.spotify_service.search_artist')
    def test_home_post_spotify_exception_handling(self, mock_search_artist, client):
        """Test exception handling when Spotify API fails."""
        mock_search_artist.side_effect = Exception('API Error')
        
        response = client.post('/', data={
            'artist_name': 'Test Artist',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200

    @patch('src.main.get_channel_stats_by_name')
    def test_home_post_youtube_channel_found(self, mock_get_channel_stats, client):
        """Test POST request with valid YouTube channel name."""
        mock_get_channel_stats.return_value = {
            'title': 'Test Channel',
            'subscribers': '1,000',
            'views': '50,000',
            'video_count': '10',
            'image_url': 'http://example.com/thumb.jpg',
            'channel_url': 'http://youtube.com/channel/abc',
        }
        
        response = client.post('/', data={
            'channel_name': 'Test Channel',
            'action': 'youtube'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Test Channel' in response.data
        mock_get_channel_stats.assert_called_once()

    @patch('src.main.get_channel_stats_by_name')
    def test_home_post_youtube_channel_not_found(self, mock_get_channel_stats, client):
        """Test POST request when YouTube channel is not found."""
        mock_get_channel_stats.return_value = None
        
        response = client.post('/', data={
            'channel_name': 'Nonexistent Channel',
            'action': 'youtube'
        }, follow_redirects=True)
        
        assert response.status_code == 200

    @patch('src.main.get_channel_stats_by_name')
    def test_home_post_youtube_exception_handling(self, mock_get_channel_stats, client):
        """Test exception handling when YouTube API fails."""
        mock_get_channel_stats.side_effect = Exception('API Error')
        
        response = client.post('/', data={
            'channel_name': 'Test Channel',
            'action': 'youtube'
        }, follow_redirects=True)
        
        assert response.status_code == 200

    def test_home_post_clear_action(self, client):
        """Test clear action to reset session."""
        # First set some session data
        with client.session_transaction() as session:
            session['artist'] = {'name': 'Test Artist'}
            session['yt_stats'] = {'title': 'Test Channel'}
        
        response = client.post('/', data={
            'action': 'clear'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify session is cleared
        with client.session_transaction() as session:
            assert 'artist' not in session
            assert 'yt_stats' not in session

    def test_home_post_empty_artist_name(self, client):
        """Test POST request with empty artist name."""
        response = client.post('/', data={
            'artist_name': '',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200

    def test_home_post_empty_channel_name(self, client):
        """Test POST request with empty channel name."""
        response = client.post('/', data={
            'channel_name': '',
            'action': 'youtube'
        }, follow_redirects=True)
        
        assert response.status_code == 200


class TestLoginRoute:
    """Test cases for the login route."""

    def test_login_get_request(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data or b'Login' in response.data

    def test_login_post_request(self, client):
        """Test POST request to login page."""
        response = client.post('/login', data={}, follow_redirects=True)
        assert response.status_code == 200


class TestAppConfiguration:
    """Test cases for application configuration."""

    def test_app_secret_key_set(self):
        """Test that secret key is configured."""
        assert app.secret_key is not None
        assert app.secret_key != ''

    def test_app_testing_mode(self, client):
        """Test that app can be set to testing mode."""
        assert app.config['TESTING'] == True

    @patch.dict(os.environ, {'APP_ENV': 'development'})
    def test_development_config(self):
        """Test development configuration."""
        # This test would require reloading the app, which is complex
        # Just verify the config object exists
        from src.config import DevelopmentConfig
        assert DevelopmentConfig.DEBUG == True

    @patch.dict(os.environ, {'APP_ENV': 'production'})
    def test_production_config(self):
        """Test production configuration."""
        from src.config import ProductionConfig
        assert ProductionConfig.DEBUG == False

    @patch.dict(os.environ, {'APP_ENV': 'preproduction'})
    def test_preproduction_config(self):
        """Test preproduction configuration."""
        from src.config import PreproductionConfig
        assert PreproductionConfig.DEBUG == False
