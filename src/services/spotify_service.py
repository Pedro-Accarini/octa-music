import os
import spotipy
import logging
from spotipy.oauth2 import SpotifyClientCredentials
from src.config import Config
from src.cache_config import CacheConfig, cache_result

logger = logging.getLogger(__name__)


class SpotifyService:
    def __init__(self, cache_instance=None):
        """
        Initialize Spotify service with optional caching support.
        
        Args:
            cache_instance: Flask-Caching cache instance for caching API responses
        """
        client_id = Config.SPOTIPY_CLIENT_ID
        client_secret = Config.SPOTIPY_CLIENT_SECRET
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.cache = cache_instance
        logger.info("SpotifyService initialized with caching support")

    def search_artist(self, artist_name):
        """
        Search for an artist on Spotify with caching support.
        
        Args:
            artist_name: Name of the artist to search for
        
        Returns:
            Dictionary with artist information or None if not found
        """
        if self.cache:
            return self._search_artist_cached(artist_name)
        return self._search_artist_uncached(artist_name)
    
    def _search_artist_cached(self, artist_name):
        """Search artist with caching enabled."""
        @cache_result(self.cache, CacheConfig.SPOTIFY_ARTIST_CACHE_TIMEOUT, "spotify:artist")
        def _cached_search(name):
            return self._search_artist_uncached(name)
        
        return _cached_search(artist_name)
    
    def _search_artist_uncached(self, artist_name):
        """Perform the actual Spotify API search without caching."""
        try:
            logger.debug(f"Searching Spotify for artist: {artist_name}")
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            if results['artists']['items']:
                a = results['artists']['items'][0]
                artist_data = {
                    'name': a['name'],
                    'followers': f"{a['followers']['total']:,}",
                    'popularity': a['popularity'],
                    'image_url': a['images'][0]['url'] if a['images'] else None,
                    'genres': ', '.join(a.get('genres', [])) if a.get('genres') else None,
                    'spotify_url': a['external_urls']['spotify'] if 'external_urls' in a and 'spotify' in a['external_urls'] else None,
                }
                logger.info(f"Found artist: {artist_data['name']}")
                return artist_data
            logger.info(f"No artist found for: {artist_name}")
            return None
        except Exception as e:
            logger.error(f"Error searching for artist {artist_name}: {e}")
            raise
