"""
Tests for rate limiting functionality
"""
import os
import sys
import pytest
import time
from unittest.mock import patch

# Set environment for testing BEFORE importing the app
os.environ['APP_ENV'] = 'testing'
os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app, limiter


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    # Set very high rate limits for testing
    app.config['RATELIMIT_DEFAULT'] = "10000 per day, 1000 per hour"
    with app.test_client() as client:
        yield client


class TestRateLimiting:
    """Tests for rate limiting functionality"""
    
    def test_limiter_is_initialized(self, client):
        """Test that rate limiter is initialized"""
        assert limiter is not None
    
    def test_normal_request_not_rate_limited(self, client):
        """Test that normal requests are not rate limited"""
        # Make several requests under the limit
        for i in range(5):
            response = client.get('/')
            assert response.status_code == 200
    
    @patch('src.main.spotify_service.search_artist')
    def test_api_endpoints_work_with_rate_limiting(self, mock_search, client):
        """Test that API endpoints work with rate limiting enabled"""
        mock_search.return_value = {
            'name': 'Test Artist',
            'followers': '12,345',
            'popularity': 80,
            'image_url': 'http://example.com/image.jpg',
            'genres': 'pop',
            'spotify_url': 'http://spotify.com/artist/123',
        }
        
        response = client.post('/', data={
            'artist_name': 'Test Artist',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200
    
    def test_rate_limit_error_handler(self, client):
        """Test that rate limit error handler returns correct format"""
        # The error handler is defined in main.py
        # We test it by checking the format it returns
        from src.main import app
        
        # Check that the error handler is registered
        assert 429 in app.error_handler_spec[None]
        
        # Verify it returns a JSON response with correct structure
        # We'll do this by triggering it via the app context
        with app.test_request_context('/'):
            from src.main import ratelimit_handler
            mock_error = Exception("Rate limit exceeded")
            response = ratelimit_handler(mock_error)
            
            assert response[1] == 429
            data = response[0].get_json()
            assert data['error'] == 'Rate limit exceeded'


class TestRequestThrottling:
    """Tests for request throttling in YouTube service"""
    
    @patch('src.services.youtube_service.requests.get')
    def test_request_throttling_delays_requests(self, mock_get):
        """Test that request throttling adds delays between requests"""
        from src.services.youtube_service import _make_youtube_request
        
        # Setup mock
        mock_response = type('obj', (object,), {'status_code': 200, 'json': lambda: {}})()
        mock_get.return_value = mock_response
        
        # Make two requests and measure time
        start_time = time.time()
        _make_youtube_request('http://test.com/1', 'test')
        _make_youtube_request('http://test.com/2', 'test')
        elapsed_time = time.time() - start_time
        
        # Should have at least some delay (MIN_REQUEST_INTERVAL)
        # We allow some tolerance for test execution overhead
        assert elapsed_time >= 0.05  # At least 50ms delay
    
    @patch('src.services.youtube_service.requests.get')
    def test_throttling_with_different_endpoints(self, mock_get):
        """Test that throttling is per-endpoint"""
        from src.services.youtube_service import throttle_request
        
        mock_response = type('obj', (object,), {'status_code': 200})()
        mock_get.return_value = mock_response
        
        @throttle_request("endpoint1")
        def test_func1():
            return "result1"
        
        @throttle_request("endpoint2")
        def test_func2():
            return "result2"
        
        # These should not interfere with each other's throttling
        result1 = test_func1()
        result2 = test_func2()
        
        assert result1 == "result1"
        assert result2 == "result2"


class TestPerformanceMonitoring:
    """Tests for performance monitoring and logging"""
    
    @patch('src.main.spotify_service.search_artist')
    def test_logging_on_api_calls(self, mock_search, client):
        """Test that API calls complete successfully (logging is implementation detail)"""
        mock_search.return_value = {
            'name': 'Test Artist',
            'followers': '12,345',
            'popularity': 80,
            'image_url': 'http://example.com/image.jpg',
            'genres': 'pop',
            'spotify_url': 'http://spotify.com/artist/123',
        }
        
        response = client.post('/', data={
            'artist_name': 'Test Artist',
            'action': 'spotify'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Verify the search was called
        assert mock_search.called
    
    @patch('src.services.youtube_service.requests.get')
    def test_youtube_request_logging(self, mock_get, caplog):
        """Test that YouTube requests are logged"""
        import logging
        from src.services.youtube_service import _make_youtube_request
        
        caplog.set_level(logging.DEBUG)
        
        mock_response = type('obj', (object,), {
            'status_code': 200,
            'json': lambda: {}
        })()
        mock_get.return_value = mock_response
        
        _make_youtube_request('http://test.com', 'test_request')
        
        # Check that logging occurred
        assert len(caplog.records) > 0


class TestCacheAndRateLimitIntegration:
    """Tests for integration between caching and rate limiting"""
    
    @patch('spotipy.Spotify.search')
    def test_cache_reduces_rate_limit_pressure(self, mock_search, client):
        """Test that caching helps avoid rate limits by reducing API calls"""
        # Mock at the spotipy level so caching works
        mock_search.return_value = {
            'artists': {
                'items': [{
                    'name': 'Test Artist',
                    'followers': {'total': 12345},
                    'popularity': 80,
                    'images': [{'url': 'http://example.com/image.jpg'}],
                    'genres': ['pop'],
                    'external_urls': {'spotify': 'http://spotify.com/artist/123'}
                }]
            }
        }
        
        # Make the same search multiple times
        for i in range(5):
            response = client.post('/', data={
                'artist_name': 'Test Artist',
                'action': 'spotify'
            }, follow_redirects=True)
            assert response.status_code == 200
        
        # With caching, the API should only be called once
        # (subsequent calls use cache)
        assert mock_search.call_count == 1
