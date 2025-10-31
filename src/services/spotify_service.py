import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from src.config import Config

class SpotifyService:
    def __init__(self):
        client_id = Config.SPOTIPY_CLIENT_ID
        client_secret = Config.SPOTIPY_CLIENT_SECRET
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def search_artist(self, artist_name):
        results = self.sp.search(q=artist_name, type='artist', limit=1)
        if results['artists']['items']:
            a = results['artists']['items'][0]
            return {
                'name': a['name'],
                'followers': f"{a['followers']['total']:,}",
                'popularity': a['popularity'],
                'image_url': a['images'][0]['url'] if a['images'] else None,
                'genres': ', '.join(a.get('genres', [])) if a.get('genres') else None,
                'spotify_url': a['external_urls']['spotify'] if 'external_urls' in a and 'spotify' in a['external_urls'] else None,
            }
        return None

    def advanced_search(self, query, search_type='track,artist,album', limit=10, offset=0):
        """
        Perform advanced search across multiple types
        
        Args:
            query: Search query string
            search_type: Comma-separated list of types (track, artist, album)
            limit: Number of results per type
            offset: Offset for pagination
        
        Returns:
            Dictionary with results for each search type
        """
        if not query:
            return {'tracks': [], 'artists': [], 'albums': []}
        
        results = self.sp.search(q=query, type=search_type, limit=limit, offset=offset)
        
        response = {}
        
        # Process tracks
        if 'tracks' in results:
            response['tracks'] = [{
                'id': t['id'],
                'name': t['name'],
                'artists': ', '.join([a['name'] for a in t['artists']]),
                'album': t['album']['name'],
                'duration_ms': t['duration_ms'],
                'popularity': t['popularity'],
                'image_url': t['album']['images'][0]['url'] if t['album']['images'] else None,
                'spotify_url': t['external_urls']['spotify'],
                'preview_url': t.get('preview_url'),
                'type': 'track'
            } for t in results['tracks']['items']]
        
        # Process artists
        if 'artists' in results:
            response['artists'] = [{
                'id': a['id'],
                'name': a['name'],
                'followers': a['followers']['total'],
                'popularity': a['popularity'],
                'image_url': a['images'][0]['url'] if a['images'] else None,
                'genres': ', '.join(a.get('genres', [])) if a.get('genres') else 'N/A',
                'spotify_url': a['external_urls']['spotify'],
                'type': 'artist'
            } for a in results['artists']['items']]
        
        # Process albums
        if 'albums' in results:
            response['albums'] = [{
                'id': al['id'],
                'name': al['name'],
                'artists': ', '.join([a['name'] for a in al['artists']]),
                'release_date': al['release_date'],
                'total_tracks': al['total_tracks'],
                'image_url': al['images'][0]['url'] if al['images'] else None,
                'spotify_url': al['external_urls']['spotify'],
                'type': 'album'
            } for al in results['albums']['items']]
        
        return response

    def get_autocomplete_suggestions(self, query, limit=5):
        """
        Get autocomplete suggestions for a query
        
        Args:
            query: Partial search query
            limit: Number of suggestions to return
        
        Returns:
            List of suggestion strings
        """
        if not query or len(query) < 2:
            return []
        
        try:
            results = self.sp.search(q=query, type='artist,track', limit=limit)
            suggestions = []
            
            # Add unique artist names
            for artist in results.get('artists', {}).get('items', []):
                if artist['name'] not in suggestions:
                    suggestions.append(artist['name'])
            
            # Add unique track names
            for track in results.get('tracks', {}).get('items', []):
                track_name = f"{track['name']} - {track['artists'][0]['name']}"
                if track_name not in suggestions and len(suggestions) < limit:
                    suggestions.append(track_name)
            
            return suggestions[:limit]
        except Exception as e:
            print(f"Error getting autocomplete suggestions: {e}")
            return []
