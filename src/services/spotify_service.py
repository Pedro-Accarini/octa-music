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
    
    def search_tracks(self, query, limit=10):
        """Search for tracks on Spotify"""
        results = self.sp.search(q=query, type='track', limit=limit)
        tracks = []
        if results['tracks']['items']:
            for t in results['tracks']['items']:
                track = {
                    'id': t['id'],
                    'name': t['name'],
                    'artist': ', '.join([artist['name'] for artist in t['artists']]),
                    'album': t['album']['name'],
                    'duration_ms': t['duration_ms'],
                    'image_url': t['album']['images'][0]['url'] if t['album']['images'] else None,
                    'spotify_url': t['external_urls']['spotify'] if 'external_urls' in t and 'spotify' in t['external_urls'] else None,
                    'preview_url': t.get('preview_url')
                }
                tracks.append(track)
        return tracks
    
    def get_track(self, track_id):
        """Get track details by Spotify track ID"""
        try:
            t = self.sp.track(track_id)
            return {
                'id': t['id'],
                'name': t['name'],
                'artist': ', '.join([artist['name'] for artist in t['artists']]),
                'album': t['album']['name'],
                'duration_ms': t['duration_ms'],
                'image_url': t['album']['images'][0]['url'] if t['album']['images'] else None,
                'spotify_url': t['external_urls']['spotify'] if 'external_urls' in t and 'spotify' in t['external_urls'] else None,
                'preview_url': t.get('preview_url')
            }
        except Exception:
            return None
