import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

os.environ['SPOTIPY_CLIENT_ID'] = 'test_client_id'
os.environ['SPOTIPY_CLIENT_SECRET'] = 'test_client_secret'

from src.services.spotify_service import SpotifyService


class TestSpotifyService:
    """Integration tests for SpotifyService."""

    @pytest.fixture
    def mock_spotify(self):
        """Create a mock Spotify client."""
        with patch('src.services.spotify_service.spotipy.Spotify') as mock_sp:
            yield mock_sp

    @pytest.fixture
    def spotify_service(self, mock_spotify):
        """Create a SpotifyService instance with mocked Spotify client."""
        service = SpotifyService()
        return service

    def test_service_initialization(self, spotify_service):
        """Test that SpotifyService initializes correctly."""
        assert spotify_service is not None
        assert hasattr(spotify_service, 'sp')

    def test_search_artist_found(self, spotify_service, mock_spotify):
        """Test searching for an artist that exists."""
        # Mock the search response
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'Taylor Swift',
                    'followers': {'total': 10000000},
                    'popularity': 95,
                    'images': [{'url': 'http://example.com/image.jpg'}],
                    'genres': ['pop', 'country'],
                    'external_urls': {'spotify': 'http://spotify.com/artist/123'}
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('Taylor Swift')
        
        assert result is not None
        assert result['name'] == 'Taylor Swift'
        assert result['followers'] == '10,000,000'
        assert result['popularity'] == 95
        assert result['image_url'] == 'http://example.com/image.jpg'
        assert result['genres'] == 'pop, country'
        assert result['spotify_url'] == 'http://spotify.com/artist/123'
        
        spotify_service.sp.search.assert_called_once_with(q='Taylor Swift', type='artist', limit=1)

    def test_search_artist_not_found(self, spotify_service, mock_spotify):
        """Test searching for an artist that doesn't exist."""
        mock_response = {
            'artists': {
                'items': []
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('Nonexistent Artist')
        
        assert result is None
        spotify_service.sp.search.assert_called_once_with(q='Nonexistent Artist', type='artist', limit=1)

    def test_search_artist_no_images(self, spotify_service, mock_spotify):
        """Test artist search when no images are available."""
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'Unknown Artist',
                    'followers': {'total': 100},
                    'popularity': 20,
                    'images': [],
                    'genres': [],
                    'external_urls': {'spotify': 'http://spotify.com/artist/456'}
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('Unknown Artist')
        
        assert result is not None
        assert result['name'] == 'Unknown Artist'
        assert result['image_url'] is None
        assert result['genres'] is None

    def test_search_artist_no_genres(self, spotify_service, mock_spotify):
        """Test artist search when genres are not available."""
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'New Artist',
                    'followers': {'total': 500},
                    'popularity': 30,
                    'images': [{'url': 'http://example.com/new.jpg'}],
                    'genres': [],
                    'external_urls': {'spotify': 'http://spotify.com/artist/789'}
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('New Artist')
        
        assert result is not None
        assert result['genres'] is None

    def test_search_artist_missing_external_urls(self, spotify_service, mock_spotify):
        """Test artist search when external URLs are missing."""
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'Local Artist',
                    'followers': {'total': 50},
                    'popularity': 10,
                    'images': [{'url': 'http://example.com/local.jpg'}],
                    'genres': ['indie']
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('Local Artist')
        
        assert result is not None
        assert result['spotify_url'] is None

    def test_search_artist_with_special_characters(self, spotify_service, mock_spotify):
        """Test artist search with special characters in name."""
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'AC/DC',
                    'followers': {'total': 5000000},
                    'popularity': 85,
                    'images': [{'url': 'http://example.com/acdc.jpg'}],
                    'genres': ['rock', 'hard rock'],
                    'external_urls': {'spotify': 'http://spotify.com/artist/acdc'}
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('AC/DC')
        
        assert result is not None
        assert result['name'] == 'AC/DC'

    def test_search_artist_api_exception(self, spotify_service, mock_spotify):
        """Test handling of API exceptions."""
        spotify_service.sp.search = MagicMock(side_effect=Exception('API Error'))
        
        with pytest.raises(Exception):
            spotify_service.search_artist('Test Artist')

    def test_search_artist_empty_name(self, spotify_service, mock_spotify):
        """Test searching with empty artist name."""
        mock_response = {
            'artists': {
                'items': []
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('')
        
        assert result is None

    def test_search_artist_number_formatting(self, spotify_service, mock_spotify):
        """Test that follower count is formatted with commas."""
        mock_response = {
            'artists': {
                'items': [{
                    'name': 'Popular Artist',
                    'followers': {'total': 123456789},
                    'popularity': 90,
                    'images': [{'url': 'http://example.com/popular.jpg'}],
                    'genres': ['pop'],
                    'external_urls': {'spotify': 'http://spotify.com/artist/popular'}
                }]
            }
        }
        
        spotify_service.sp.search = MagicMock(return_value=mock_response)
        
        result = spotify_service.search_artist('Popular Artist')
        
        assert result is not None
        assert result['followers'] == '123,456,789'
