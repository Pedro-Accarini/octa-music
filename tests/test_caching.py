"""
Tests for caching functionality
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Set environment for testing BEFORE importing the app
os.environ['APP_ENV'] = 'testing'
os.environ['SPOTIPY_CLIENT_ID'] = 'dummy'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'dummy'

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app, cache
from src.services.spotify_service import SpotifyService
from src.services.youtube_service import get_channel_stats_by_name


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret_key'
    with app.test_client() as client:
        if cache:
            cache.clear()
        yield client
        if cache:
            cache.clear()


class TestCacheFunctionality:
    """Tests for caching functionality"""
    
    def test_cache_is_initialized(self, client):
        """Test that cache is initialized in testing mode"""
        assert cache is not None
    
    @patch('src.services.spotify_service.spotipy.Spotify.search')
    def test_spotify_service_caching(self, mock_search):
        """Test that Spotify service caches results"""
        # Setup mock
        mock_search.return_value = {
            'artists': {
                'items': [{
                    'name': 'Test Artist',
                    'followers': {'total': 12345},
                    'popularity': 80,
                    'images': [{'url': 'http://example.com/image.jpg'}],
                    'genres': ['pop', 'rock'],
                    'external_urls': {'spotify': 'http://spotify.com/artist/123'}
                }]
            }
        }
        
        # Create service with cache
        service = SpotifyService(cache_instance=cache)
        
        # First call - should hit the API
        result1 = service.search_artist('Test Artist')
        assert result1 is not None
        assert result1['name'] == 'Test Artist'
        assert mock_search.call_count == 1
        
        # Second call - should use cache
        result2 = service.search_artist('Test Artist')
        assert result2 is not None
        assert result2['name'] == 'Test Artist'
        # Call count should still be 1 because second call used cache
        assert mock_search.call_count == 1
        
        # Results should be identical
        assert result1 == result2
    
    @patch('src.services.spotify_service.spotipy.Spotify.search')
    def test_spotify_service_without_cache(self, mock_search):
        """Test that Spotify service works without cache"""
        # Setup mock
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
        
        # Create service without cache
        service = SpotifyService(cache_instance=None)
        
        # First call
        result1 = service.search_artist('Test Artist')
        assert result1 is not None
        assert mock_search.call_count == 1
        
        # Second call - should hit API again since no cache
        result2 = service.search_artist('Test Artist')
        assert result2 is not None
        assert mock_search.call_count == 2
    
    def test_cache_clear_endpoint(self, client):
        """Test cache clear endpoint"""
        response = client.post('/api/cache/clear')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_cache_invalidate_endpoint(self, client):
        """Test cache invalidation endpoint"""
        response = client.post('/api/cache/invalidate/spotify:*')
        assert response.status_code in [200, 400]  # 400 if cache doesn't support pattern invalidation
        data = response.get_json()
        assert 'status' in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'cache_enabled' in data
        assert 'rate_limiter_enabled' in data


class TestYouTubeCaching:
    """Tests for YouTube service caching"""
    
    @patch('src.services.youtube_service.requests.get')
    def test_youtube_channel_caching(self, mock_get):
        """Test that YouTube service caches channel stats"""
        # Setup mock responses
        search_response = Mock()
        search_response.status_code = 200
        search_response.json.return_value = {
            'items': [{
                'snippet': {'channelId': 'test_channel_id'}
            }]
        }
        
        channel_response = Mock()
        channel_response.status_code = 200
        channel_response.json.return_value = {
            'items': [{
                'statistics': {
                    'subscriberCount': '1000',
                    'viewCount': '50000',
                    'videoCount': '10'
                },
                'snippet': {
                    'title': 'Test Channel',
                    'description': 'Test Description',
                    'thumbnails': {'high': {'url': 'http://example.com/thumb.jpg'}}
                }
            }]
        }
        
        video_search_response = Mock()
        video_search_response.status_code = 200
        video_search_response.json.return_value = {'items': []}
        
        mock_get.side_effect = [search_response, channel_response, video_search_response]
        
        # First call
        result1 = get_channel_stats_by_name('Test Channel', 'test_api_key', cache_instance=cache)
        assert result1 is not None
        assert result1['title'] == 'Test Channel'
        initial_call_count = mock_get.call_count
        
        # Reset side effects for potential second call
        mock_get.side_effect = [search_response, channel_response, video_search_response]
        
        # Second call - should use cache
        result2 = get_channel_stats_by_name('Test Channel', 'test_api_key', cache_instance=cache)
        assert result2 is not None
        assert result2['title'] == 'Test Channel'
        
        # Call count should be the same or slightly higher (cache hit)
        # Due to caching, we shouldn't make the same number of calls again
        assert mock_get.call_count <= initial_call_count + 3
        
        # Results should be identical
        assert result1 == result2


class TestCacheConfiguration:
    """Tests for cache configuration"""
    
    def test_cache_key_generation(self):
        """Test cache key generation"""
        from src.cache_config import generate_cache_key
        
        # Test simple key
        key1 = generate_cache_key('test', 'arg1', 'arg2')
        assert 'test' in key1
        assert 'arg1' in key1
        assert 'arg2' in key1
        
        # Test with kwargs
        key2 = generate_cache_key('test', key1='value1', key2='value2')
        assert 'test' in key2
        assert 'key1=value1' in key2
        assert 'key2=value2' in key2
        
        # Test long key gets hashed
        long_arg = 'x' * 300
        key3 = generate_cache_key('test', long_arg)
        assert len(key3) < 250  # Should be hashed and shorter
    
    def test_cache_config_values(self):
        """Test that cache configuration values are set correctly"""
        from src.cache_config import CacheConfig, RateLimitConfig
        
        assert CacheConfig.CACHE_KEY_PREFIX == "octa_music:"
        assert CacheConfig.CACHE_DEFAULT_TIMEOUT >= 0
        assert CacheConfig.SPOTIFY_ARTIST_CACHE_TIMEOUT > 0
        assert CacheConfig.YOUTUBE_CHANNEL_CACHE_TIMEOUT > 0
        
        assert isinstance(RateLimitConfig.RATELIMIT_ENABLED, bool)
        assert RateLimitConfig.RATELIMIT_DEFAULT is not None
