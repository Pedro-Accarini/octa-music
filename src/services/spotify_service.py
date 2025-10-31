import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from src.config import Config
import logging

logger = logging.getLogger(__name__)

class SpotifyService:
    def __init__(self):
        client_id = Config.SPOTIPY_CLIENT_ID
        client_secret = Config.SPOTIPY_CLIENT_SECRET
        
        if not client_id or not client_secret:
            logger.warning("Spotify credentials not configured")
            raise ValueError("Spotify credentials not configured")
        
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def search_artist(self, artist_name):
        """Search for an artist on Spotify.
        
        Args:
            artist_name: The name of the artist to search for
            
        Returns:
            dict: Artist information or None if not found
            
        Raises:
            SpotifyException: If there's an error with the Spotify API
        """
        try:
            if not artist_name or not artist_name.strip():
                logger.warning("Empty artist name provided")
                return None
            
            results = self.sp.search(q=artist_name, type='artist', limit=1)
            
            if results and results.get('artists') and results['artists'].get('items'):
                a = results['artists']['items'][0]
                return {
                    'name': a['name'],
                    'followers': f"{a['followers']['total']:,}",
                    'popularity': a['popularity'],
                    'image_url': a['images'][0]['url'] if a['images'] else None,
                    'genres': ', '.join(a.get('genres', [])) if a.get('genres') else None,
                    'spotify_url': a['external_urls']['spotify'] if 'external_urls' in a and 'spotify' in a['external_urls'] else None,
                }
            
            logger.info(f"No artist found for: {artist_name}")
            return None
            
        except SpotifyException as e:
            logger.error(f"Spotify API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in search_artist: {str(e)}")
            raise
